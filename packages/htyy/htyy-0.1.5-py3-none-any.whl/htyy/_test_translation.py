import requests
from googletrans import Translator
from functools import lru_cache
from abc import ABC, abstractmethod

# ====================
# 基础函数版本
# ====================

def translate_text(text: str, target_lang: str = 'en', source_lang: str = 'auto') -> str:
    """
    使用googletrans进行免费翻译
    适用于简单需求
    """
    try:
        translator = Translator()
        result = translator.translate(text, dest=target_lang, src=source_lang)
        return result.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

# ====================
# 类版本（带缓存）
# ====================

class TranslationService(ABC):
    """翻译服务抽象基类"""
    @abstractmethod
    def translate(self, text: str, target_lang: str) -> str:
        pass

from translate import Translator

class FreeTranslator(TranslationService):
    def __init__(self, text, from_lang='auto', to_lang='zh'):
        self.translator = Translator(from_lang=from_lang, to_lang=to_lang)
        translate_text(text=text, target_lang=to_lang, source_lang=from_lang)
    
    def translate(self, text: str, target_lang: str) -> str:
        try:
            return self.translator.translate(text)
        except Exception as e:
            print(f"Translate error: {e}")
            return text

class GoogleTranslator(TranslationService):
    """Google翻译实现"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://translation.googleapis.com/language/translate/v2"
        
    @lru_cache(maxsize=1024)  # 缓存最近翻译结果
    def translate(self, text: str, target_lang: str = 'en') -> str:
        try:
            if self.api_key:
                # 使用官方API（需要API密钥）
                params = {
                    'q': text,
                    'target': target_lang,
                    'key': self.api_key
                }
                response = requests.post(self.base_url, params=params)
                return response.json()['data']['translations'][0]['translatedText']
            else:
                # 回退到免费库
                return translate_text(text, target_lang)
        except Exception as e:
            print(f"Google translation failed: {e}")
            return text

class DeepLTranslator(TranslationService):
    def __init__(self):
        self.endpoint = "https://api-free.deepl.com/v2/translate"
    
    def translate(self, text: str, target_lang: str) -> str:
        params = {
            'auth_key': 'free_key',
            'text': text,
            'target_lang': target_lang
        }
        response = requests.post(self.endpoint, data=params)
        return response.json()['translations'][0]['text']
    
import argostranslate.translate

class ArgosTranslator(TranslationService):
    def __init__(self, from_code='zh', to_code='en'):
        self.from_code = from_code
        self.to_code = to_code
    
    def translate(self, text: str) -> str:
        return argostranslate.translate.translate(text, self.from_code, self.to_code)

from transformers import pipeline

class HelsinkiTranslator(TranslationService):
    def __init__(self):
        self.translator = pipeline("translation", model="Helsinki-NLP/opus-mt-zh-en")
    
    def translate(self, text: str) -> str:
        return self.translator(text)[0]['translation_text']

class BatchTranslator:
    """批量翻译处理器"""
    
    def __init__(self, service: TranslationService):
        self.service = service
        
    def translate_batch(self, texts: list, target_lang: str) -> list:
        return [self.service.translate(text, target_lang) for text in texts]

# ====================
# 高级版本（支持多服务）
# ====================

class TranslationServiceFactory:
    """翻译服务工厂"""
    
    @staticmethod
    def get_service(service_name: str, **kwargs) -> TranslationService:
        services = {
            'google': GoogleTranslator,
            "deepl":DeepLTranslator,
            "argos": ArgosTranslator,
            "helsinki": HelsinkiTranslator
        }
        return services[service_name.lower()](**kwargs)

# ====================
# 使用示例
# ====================

if __name__ == "__main__":
    print(FreeTranslator("Hello word!"))
    