import rclpy
from rclpy.node import Node
from autopilot_interfaces.srv import SpeachText
import espeakng

class Speaker(Node):
    def __init__(self):
        super().__init__('speaker')
        self.speach_service_ = self.create_service(SpeachText, 'speach_text', self.speach_text_callback)
        # self.speech_service_.start()
        # self.speech_service_.wait_for_service()
        self.speaker_ = espeakng.Speaker()
        # 尝试设置语音，如果失败则使用默认语音
        # try:
        #     # 不同版本的espeakng库API可能不同
        #     if hasattr(self.speaker_, 'set_voice'):
        #         self.speaker_.set_voice('zh-CN')
        #     elif hasattr(self.speaker_, 'voice'):
        #         self.speaker_.voice = 'zh-CN'
        # except Exception as e:
        #     self.get_logger().warning(f"设置语音失败: {str(e)}")
        #self.speaker_.voice = 'zh'
        self.speaker_.voice = 'zh-CN'
        #self.speaker_.voice = 'cmn-latn-pinyin'
        
        # 尝试设置音量，如果失败则使用默认音量
        # try:
        #     if hasattr(self.speaker_, 'set_volume'):
        #         self.speaker_.set_volume(0.5)
        #     elif hasattr(self.speaker_, 'volume'):
        #         self.speaker_.volume = 0.5
        # except Exception as e:
        #     self.get_logger().warning(f"设置音量失败: {str(e)}")
        self.speaker_.volume = 0.5

    def speach_text_callback(self, request, response):
        self.get_logger().info(f"正在准备朗读: {request.text}")
        self.speaker_.say(request.text)
        self.speaker_.wait()
        self.get_logger().info(f"朗读完成: {request.text}")
        response.result = True
        return response

def main():
    rclpy.init()
    speaker = Speaker()
    rclpy.spin(speaker) 
    rclpy.shutdown()
