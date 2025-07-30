import asyncio
import base64
import json
import re
import time
import uuid
import io
from typing import Dict, List, Optional
import aiohttp
import tempfile
import os
from aiohttp import ClientWebSocketResponse

from pydantic import BaseModel, ConfigDict, Field

from kirara_ai.config.config_loader import CONFIG_FILE, ConfigJsonSchema, ConfigLoader
from kirara_ai.config.global_config import GlobalConfig
from kirara_ai.im.adapter import BotProfileAdapter, IMAdapter
from kirara_ai.im.message import (ImageMessage, IMMessage, MessageElement, TextMessage,VoiceMessage,VideoElement,MentionElement)
from kirara_ai.im.profile import UserProfile
from kirara_ai.im.sender import ChatSender, ChatType
from kirara_ai.logger import get_logger
from kirara_ai.web.app import WebServer
from kirara_ai.workflow.core.dispatch import WorkflowDispatcher

# 导入处理视频所需的库
from moviepy.video.io.VideoFileClip import VideoFileClip

class WeChatConfig(BaseModel):
    """
    WeChat 配置文件模型。
    """
    api_base_url: str = Field(title="API主机地址加端口", description="WeChat HTTP API 的主机地址", default="http://localhost:1239")
    auth_key: Optional[str] = Field(
        title="授权码", description="API接口的授权码，如果为空则会自动获取。", default=None)
    admin_key: str = Field(
        title="Admin Key", description="用于生成授权码的管理员密钥，默认为12345。", default="12345")

    model_config = ConfigDict(extra="allow")


class WeChatAdapter(IMAdapter, BotProfileAdapter):
    """
    WeChat Adapter，包含 WeChat Bot 的所有逻辑。
    """

    dispatcher: WorkflowDispatcher
    web_server: WebServer
    _loop: asyncio.AbstractEventLoop
    _session: aiohttp.ClientSession
    is_running: bool = False

    def __init__(self, config: WeChatConfig):
        self.config = config
        self.logger = get_logger("WeChat-Adapter")
        self.auth_key = config.auth_key
        self.admin_key = config.admin_key
        self.api_base_url = config.api_base_url
        self.wxid = None
        self._running_task = None

    async def _get_auth_key(self) -> str:
        """
        获取授权码
        """
        if self.auth_key:
            return self.auth_key
        payload = {
            "Count": 1,
            "Days": 9999999
        }
        url = f"{self.api_base_url}/admin/GenAuthKey1?key={self.admin_key}"
        async with self._session.post(url,json=payload) as response:
            data = await response.json()
            if data.get("Code") == 200 and data.get("Data"):
                self.auth_key = data["Data"][0]
                self.logger.info(f"获取授权码成功: {self.auth_key}")
                return self.auth_key
            else:
                raise Exception(f"获取授权码失败: {data}")
    async def _check_login_status(self):
        auth_key = await self._get_auth_key()
        url = f"{self.api_base_url}/user/GetProfile?key={auth_key}"
        async with self._session.get(url) as response:
            data = await response.json()
            if data.get("Code") == 200 and data.get("Data"):
                self.wxid = data["Data"].get("userInfo", {}).get("userName",{}).get("str",{})
            else:
                text = data["Text"]
                self.logger.error(f"微信未登录，状态: {text}")
    async def _check_login_status(self) -> bool:
        """
        检查登录状态
        """
        auth_key = await self._get_auth_key()
        url = f"{self.api_base_url}/login/GetLoginStatus?key={auth_key}"
        payload = {"key": auth_key}
        async with self._session.get(url) as response:
            data = await response.json()
            if data.get("Code") == 200 and data.get("Data"):
                login_state = data["Data"].get("loginState", 0)
                if login_state == 1:
                    self.logger.info("微信登录状态正常")
                    return True
                else:
                    self.logger.info(f"微信未登录，状态: {login_state}")
                    return False
            else:
                text = data["Text"]
                self.logger.error(f"微信未登录，状态: {text}")
                return False

    async def _get_login_qrcode(self) -> str:
        """
        获取登录二维码
        """
        auth_key = await self._get_auth_key()
        url = f"{self.api_base_url}/login/GetLoginQrCodeNewX?key={auth_key}"
        payload = {
            "Check": False,
            "Proxy": ""
        }
        async with self._session.post(url,json=payload) as response:
            data = await response.json()
            if data.get("Code") == 200 and data.get("Data"):
                qrcode_url = data["Data"]["QrCodeUrl"]
                self.logger.info(f"获取登录二维码成功: {qrcode_url}")
                return qrcode_url
            else:
                raise Exception(f"获取登录二维码失败: {data}")

    async def _wait_for_login(self, timeout: int = 60) -> bool:
        """
        等待登录
        """
        qrcode_url = await self._get_login_qrcode()


        start_time = time.time()
        while time.time() - start_time < timeout:
            if await self._check_login_status():
                return True
            self.logger.info("请使用微信扫描以下二维码登录:")
            self.logger.info(f"二维码链接: {qrcode_url}")
            await asyncio.sleep(2)

        return False

    async def _poll_messages(self):
        """
        使用WebSocket同步获取消息
        """
        auth_key = await self._get_auth_key()
        ws_url = self.api_base_url.replace("http://", "ws://").replace("https://", "wss://") + f"/ws/GetSyncMsg?key={auth_key}"
        try:
            async with self._session.ws_connect(ws_url) as ws:
                self.logger.info(f"WebSocket已连接: {ws_url}")
                while self.is_running:
                    try:
                        msg = await ws.receive()
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            msg_item = json.loads(msg.data)
                            self.logger.debug(f"收到消息: {msg_item}")
                            if abs(time.time() - msg_item["create_time"]) <= 300:
                                await self._process_message(msg_item, msg_item["to_user_name"]["str"])
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            self.logger.error(f"WebSocket错误: {msg}")
                            break
                        elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.CLOSING):
                            self.logger.warning("WebSocket连接已关闭")
                            break
                    except Exception as e:
                        self.logger.error(f"WebSocket消息处理出错: {e}")
        except Exception as e:
            self.logger.error(f"WebSocket连接失败: {e}")
    async def getFullImageData(self, msg):
        url = f"{self.api_base_url}/message/GetMsgBigImg?key=4ee59fb5-9259-46f7-9bba-c300bfe32878"

        # Initial request parameters
        payload = {
            "CompressType": 0,
            "FromUserName": msg["from_user_name"]["str"],
            "MsgId": msg["msg_id"],
            "Section": {
                "DataLen": 65536,
                "StartPos": 0
            },
            "ToUserName": msg["to_user_name"]["str"],
            "TotalLen": 0
        }

        # Store all image data
        all_image_data = bytearray()

        # Start downloading segments
        start_pos = 0
        total_len = None

        print("Starting to download image segments...")

        while True:
            # Update start position in payload
            payload["Section"]["StartPos"] = start_pos

            # Make the request
            async with self._session.post(url,json=payload) as response:
                # Parse the response
                response_data = await response.json()

                if response_data["Code"] != 200:
                    print(f"Error: Response code {response_data['Code']}")
                    break

                # Get the image data
                data = response_data["Data"]

                # Get total length on first request
                if total_len is None:
                    total_len = data["TotalLen"]
                    print(f"Total image size: {total_len} bytes")
                    # Update TotalLen in payload
                    payload["TotalLen"] = total_len

                # Get the current segment info
                current_start_pos = data["StartPos"]
                current_data_len = data["DataLen"]

                # Decode base64 data
                base64_data = data["Data"]["Buffer"]
                image_segment = base64.b64decode(base64_data)

                # Add to our complete image data
                all_image_data.extend(image_segment)

                print(f"Downloaded segment: {current_start_pos} to {current_start_pos + current_data_len} of {total_len}")

                # Update start position for next request
                start_pos = current_start_pos + current_data_len

                # Check if we're done
                if start_pos >= total_len:
                    print("Download complete!")
                    break


        # Convert image data to base64 and save to test.txt
        return base64.b64encode(all_image_data).decode('utf-8')
    async def _process_message(self, msg, self_username):
        """
        处理收到的消息
        """
        try:
            from_username = msg["from_user_name"]["str"]
            to_username = msg["to_user_name"]["str"]
            msg_type = msg["msg_type"]
            content = msg.get("content", {}).get("str", "")
            push_content = msg.get("push_content", {})
            msg_id = msg["msg_id"]
            create_time = msg["create_time"]

            # 过滤自己发送的消息
            if from_username == self_username:
                return

            # 判断是群聊还是私聊
            is_group = from_username.endswith("@chatroom")
            sender_name = push_content
            if ":" in  push_content:
                sender_name = push_content.split(":")[0]
            elif "在群聊中" in push_content:
                sender_name = push_content.split("在群聊中")[0]
            if is_group:
                # 群聊消息，解析发送者ID
                # 群聊消息格式通常为: "wxid_xxx:\n消息内容"
                match = re.match(r"(.*?):(.*)", content, re.DOTALL)

                if match:
                    sender_id = match.group(1).strip()
                    content = match.group(2).strip()
                    sender = ChatSender.from_group_chat(sender_id, from_username, sender_name)
                else:
                    # 如果无法解析，使用群ID作为发送者ID
                    sender = ChatSender.from_group_chat(from_username, from_username, sender_name)
            else:
                # 私聊消息
                sender = ChatSender.from_c2c_chat(from_username, sender_name)

            # 设置原始元数据
            sender.raw_metadata = {
                "message_id": msg_id,
                "create_time": create_time,
                "self_username": self_username
            }

            # 创建消息元素
            elements: List[MessageElement] = []
            msg_type = msg["msg_type"]
            if "msg_source" in msg and  to_username in msg["msg_source"]:
                elements.append(MentionElement(target=ChatSender.get_bot_sender()))
            if msg_type == 1:  # 文本消息
                elements.append(TextMessage(text=content))
            elif msg_type == 3:  # 图片消息
                img_buf = await self.getFullImageData(msg)
                if img_buf:
                    # 这里假设img_buf中包含了base64编码的图片数据
                    # 实际使用时可能需要根据API调整
                    img_data = base64.b64decode(img_buf)
                    elements.append(ImageMessage(data=img_data))
                else:
                    # 如果没有图片数据，退化为文本消息
                    elements.append(TextMessage(text="[图片]"))
            else:
                # 其他类型消息，作为文本处理
                return

            # 创建消息对象
            im_message = IMMessage(sender=sender, message_elements=elements, raw_message=msg)

            # 派发消息
            await self.dispatcher.dispatch(self, im_message)

        except Exception as e:
            self.logger.error(f"处理消息出错: {e}")

    async def convert_to_message(self, raw_message) -> IMMessage:
        """
        将原始消息转换为统一消息格式，此方法在此适配器中不使用，
        消息处理在_process_message中完成
        """
        pass

    async def send_message(self, message: IMMessage, recipient: ChatSender):
        """
        发送消息
        :param message: 要发送的消息对象。
        :param recipient: 接收消息的目标对象。
        """
        auth_key = await self._get_auth_key()
        url = f"{self.api_base_url}/message/SendTextMessage?key={auth_key}"

        # 准备发送的消息内容
        to_username = recipient.group_id if recipient.group_id else recipient.user_id

        if not to_username:
            raise ValueError("接收者ID不能为空")

        # 处理不同类型的消息元素
        if not message:
            return
        for element in message.message_elements:
            if isinstance(element, TextMessage):
                # 发送文本消息
                payload = {
                    "MsgItem": [
                        {
                            "AtWxIDList": [],
                            "ImageContent": "",
                            "MsgType": 0,
                            "TextContent": element.text,
                            "ToUserName": to_username
                        }
                    ]
                }

                async with self._session.post(url, json=payload) as response:
                    data = await response.json()
                    if data.get("Code") != 200:
                        self.logger.error(f"发送文本消息失败: {data}")

            elif isinstance(element, VoiceMessage):
                title = "音乐"
                if element.get_description():
                    title = element.get_description()
                xml = f'<appmsg appid="" sdkver="1"><title>{title}</title><des>点击收听音乐直链</des><action>view</action><type>5</type><showtype>0</showtype><content/><url>{element.url}</url><dataurl/><lowurl/><lowdataurl/><recorditem/><thumburl/><messageaction/><laninfo/><extinfo/><sourceusername/><sourcedisplayname/><commenturl/><appattach><totallen>0</totallen><attachid/><emoticonmd5></emoticonmd5><fileext/><aeskey></aeskey></appattach><webviewshared><publisherId/><publisherReqId>0</publisherReqId></webviewshared><weappinfo><pagepath/><username/><appid/><appservicetype>0</appservicetype></weappinfo><websearch/></appmsg><fromusername>{self.wxid}</fromusername><scene>0</scene><appinfo><version>1</version><appname/></appinfo><commenturl/>'
                payload = {
                    "AppList": [
                        {"ToUserName":to_username,
                         "ContentType": 5,
                         "ContentXML": xml
                         }
                    ]
                }
                url = f"{self.api_base_url}/message/SendAppMessage?key={auth_key}"
                async with self._session.post(url, json=payload) as response:
                    data = await response.json()
                    self.logger.debug(data)
                    if data.get("Code") != 200:
                        self.logger.error(f"发送语音消息失败: {data}")

            elif isinstance(element, VideoElement):


                video_data = await element.get_data()
                if not video_data:
                    self.logger.error("获取视频数据失败")
                    continue

                # 尝试获取视频第一帧作为缩略图
                thumb_data = ""

                # 先上传视频到CDN
                upload_payload = {
                    "ThumbData": thumb_data,
                    "ToUserName": to_username,
                    "VideoData": base64.b64encode(video_data).decode('utf-8')
                }

                upload_url = f"{self.api_base_url}/message/CdnUploadVideo?key={auth_key}"
                async with self._session.post(upload_url, json=upload_payload) as response:
                    upload_data = await response.json()
                    self.logger.debug(f"上传视频响应: {upload_data}")

                    if upload_data.get("Code") != 200:
                        self.logger.error(f"上传视频失败: {upload_data}")
                        continue

                    # 获取上传响应中的必要数据
                    file_id = upload_data["Data"]["FileID"]
                    aes_key = upload_data["Data"]["FileAesKey"]
                    video_size = upload_data["Data"]["VideoDataSize"]

                    # 获取视频时长
                    play_length = await self._get_video_duration(video_data)
                    self.logger.debug(f"视频时长: {play_length}秒")
                    if not play_length:
                        play_length = upload_data["Data"]["Seq"]

                    # 发送视频消息
                    forward_payload = {
                        "ForwardVideoList": [
                            {
                                "AesKey": aes_key,
                                "CdnThumbLength": 1,  # 这里使用固定值1，因为缩略图可能为空
                                "CdnVideoUrl": file_id,
                                "Length": video_size,
                                "PlayLength": play_length,
                                "ToUserName": to_username
                            }
                        ]
                    }
                    forward_url = f"{self.api_base_url}/message/ForwardVideoMessage?key={auth_key}"
                    async with self._session.post(forward_url, json=forward_payload) as forward_response:
                        forward_data = await forward_response.json()
                        self.logger.debug(f"发送视频响应: {forward_data}")
                        if forward_data.get("Code") != 200:
                            self.logger.error(f"发送视频消息失败: {forward_data}")

            elif isinstance(element, ImageMessage):
                # 发送文本消息
                media_manager = element._media_manager
                data = await media_manager.get_data(element.media_id)
                payload = {
                    "MsgItem": [
                        {
                            "AtWxIDList": [],
                            "ImageContent": base64.b64encode(data).decode('utf-8'),
                            "MsgType": 0,
                            "TextContent": "",
                            "ToUserName": to_username
                        }
                    ]
                }
                url = f"{self.api_base_url}/message/SendImageNewMessage?key={auth_key}"
                async with self._session.post(url, json=payload) as response:
                    data = await response.json()
                    if data.get("Code") != 200:
                        self.logger.error(f"发送图片消息失败: {data}")

    async def get_bot_profile(self) -> Optional[UserProfile]:
        """
        获取机器人资料
        :return: 机器人资料
        """
        if not self.auth_key:
            return None

        # 由于接口限制，这里返回一个固定的资料
        return UserProfile(
            user_id=self.auth_key,
            username="WeChat Bot",
            display_name="WeChat Bot",
            avatar_url=""
        )

    async def start(self):
        """启动 Bot"""
        self.logger.info("正在启动 WeChat 适配器...")
        self._session = aiohttp.ClientSession()
        self.is_running = True

        # 检查登录状态并处理登录
        is_logged_in = await self._check_login_status()
        if not is_logged_in:
            self.logger.info("需要登录微信，正在获取登录二维码...")
            login_success = await self._wait_for_login()
            if not login_success:
                self.logger.error("等待登录超时，启动失败")
                self.is_running = False
                await self._session.close()
                return
            else:
                config: GlobalConfig = self.dispatcher.container.resolve(GlobalConfig)
                for im in config.ims:
                    if im.adapter == "wechat" and not im.config["auth_key"]:
                        im.config["auth_key"] = self.auth_key
                        ConfigLoader.save_config_with_backup(CONFIG_FILE, config)

        # 启动消息轮询任务
        self._running_task = asyncio.create_task(self._poll_messages())
        self.logger.info("WeChat 适配器启动完成")

    async def stop(self):
        """停止 Bot"""
        self.logger.info("正在停止 WeChat 适配器...")
        self.is_running = False

        if self._running_task:
            self._running_task.cancel()
            try:
                await self._running_task
            except asyncio.CancelledError:
                pass
            self._running_task = None

        await self._session.close()
        self.logger.info("WeChat 适配器已停止")

    async def _get_video_duration(self, video_data: bytes) -> str:
        """
        获取视频时长
        :param video_data: 视频二进制数据
        :return: 视频时长（秒）
        """
        try:

            # 创建临时文件保存视频数据
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_file.write(video_data)
                temp_file_path = temp_file.name

            try:
                # 使用moviepy获取视频时长
                with VideoFileClip(temp_file_path) as clip:
                    # 返回整数时长（秒）
                    return int(clip.duration)
            finally:
                # 确保删除临时文件
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
        except Exception as e:
            self.logger.error(f"获取视频时长时出错: {e}")
            return ""  # 出错时返回空字符串
