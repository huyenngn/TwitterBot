import os
from google.cloud import translate

google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
gcloud_id = os.getenv("GCLOUD_ID")


class Translator:
    def __init__(self, src, dst, glossary={}, corrections={}):
        self.google = translate.TranslationServiceClient()
        self.glossary = glossary
        self.corrections = corrections
        self.src = src
        self.dst = dst

    def translate_text(self, text):
        if not text:
            return ""

        t = text
        for src, dst in self.glossary.items():
            t = t.replace(src, dst)

        parent = f"projects/{gcloud_id}/locations/global"

        response = self.google.translate_text(
            request={
                "parent": parent,
                "contents": [t],
                "mime_type": "text/plain",  # mime types: text/plain, text/html
                "source_language_code": self.src,
                "target_language_code": self.dst,
            }
        )

        translation = response.translations[0].translated_text

        if translation != t:
            for src, dst in self.corrections.items():
                translation = translation.replace(src, dst)

        return translation