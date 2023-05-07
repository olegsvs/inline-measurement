from transformers import MBartTokenizer, MBartForConditionalGeneration
from transformers import AutoTokenizer
import subprocess
import sys
import logging
import os
from collections import deque
from datetime import datetime

# Enable logging
logger = logging.getLogger(__name__)


class Summary:
    def __init__(self) -> None:
        #self.model_name = "IlyaGusev/mbart_ru_sum_gazeta"
        #self.tokenizer = MBartTokenizer.from_pretrained(self.model_name)
        #self.model = MBartForConditionalGeneration.from_pretrained(self.model_name)
        self.model_name = "Kirili4ik/mbart_ruDialogSum"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = MBartForConditionalGeneration.from_pretrained(self.model_name)
        self.model.eval()

    @staticmethod
    def tail(filename, n):
        result = None
        try:
            with open(filename) as f:
                result = ''.join(deque(f, n))
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error('Failed summary_internal: ' + str(e) + ", line: " + str(exc_tb.tb_lineno))
        return result


    def summary_text(self, text_file_name: str) -> str:
        summary = ''
        try:
            text = self.tail("messages/chat_" + text_file_name, 25)
            text2 = text.replace("\n", ". ")
            logger.info("Summary for text: " + text2.rstrip())
            input_ids = self.tokenizer(
                [text2.rstrip()],
                max_length=600,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )["input_ids"]

            output_ids = self.model.generate(
                input_ids=input_ids,
                top_k=0,
                num_beams=4,
                no_repeat_ngram_size=4
#    input_ids=input_ids,
#    no_repeat_ngram_size=4
            )[0]

            summary = self.tokenizer.decode(output_ids, skip_special_tokens=True)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            logger.error('Failed summary_internal: ' + str(e) + ", line: " + str(exc_tb.tb_lineno))
        return summary
