""" core 需要修改"""
import re
import os
import importlib.resources
from typing import Dict, Any
import yaml
from llmada import BianXieAdapter
from querypipz import BuilderFactory,BuilderType,Director
from agentflowz.main import AgentFactory,AgentType,EasyAgentz
from contextlib import contextmanager
import time
from .log import Log
logger = Log.logger

def load_config():
    """ load config """
    with importlib.resources.open_text('clientz', 'config.yaml') as f:
        return yaml.safe_load(f)

def format_node_for_chat(node_data: Dict[str, Any]) -> str:
    """
    解析节点数据，生成适合聊天窗口显示的格式化字符串。

    Args:
        node_data: 包含节点信息的字典结构。

    Returns:
        一个格式化的字符串，包含分数和节点文本内容。
        如果结构异常，返回错误提示。
    """
    node = node_data.get('node')
    score = node_data.get('score')

    if not node:
        return "Error: Could not find 'node' information."

    text_content = node.get('text')
    if not text_content:
        return "Error: 'text' content not found in node."

    # 移除 text 开头的 "topic:  content: \n\n\n" 或类似的元数据前缀
    # 根据你提供的样本，可能是固定的前缀，或者需要更灵活的处理
    # 这里简单移除已知的开头
    prefix_to_remove = "topic:  content: \n\n\n"
    if text_content.startswith(prefix_to_remove):
        text_content = text_content[len(prefix_to_remove):].strip()
    else:
        text_content = text_content.strip() # 或者只移除首尾空白

    # 构建输出字符串
    output = ""
    if score is not None:
        # 格式化分数，例如保留两位小数
        output += f"**Relevant Information (Score: {score:.2f})**:\n\n"
    else:
        output += "**Relevant Information:**\n\n"

    # 直接添加处理后的文本内容
    # 假设聊天窗口支持 Markdown，会渲染 #, ##, **, -, []() 等
    output += text_content

    # 你可以进一步处理 links，例如将它们提取出来单独列在末尾
    # link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    # links_found = link_pattern.findall(text_content)
    # if links_found:
    #     output += "\n\n---\n*Links mentioned:*\n"
    #     for link_text, link_url in links_found:
    #         output += f"- [{link_text}]({link_url})\n" # 或其他格式

    return output

def extract_last_user_input(dialogue_text):
    """
    从多轮对话文本中提取最后一个 user 的输入内容。

    Args:
        dialogue_text: 包含多轮对话的字符串。

    Returns:
        最后一个 user 的输入内容字符串，如果未找到则返回 None。
    """
    # 修正后的正则表达式
    # (?s) 标志：使 . 匹配换行符
    # .* 匹配任意字符，直到最后一个 user:
    # user:\s* 匹配 "user:" 后面的零个或多个空白字符
    # (.*?) 非贪婪匹配任意字符，直到下一个 user: 或字符串末尾
    # (?=user:|$) 正向先行断言：断言后面是 "user:" 或者字符串末尾
    pattern = r"(?s).*user:\s*(.*?)(?=user:|$)"

    match = re.search(pattern, dialogue_text)

    if match:
        # group(1) 捕获的是最后一个 user: 到下一个 user: 或字符串末尾的内容
        return match.group(1).strip()
    else:
        return None




@contextmanager
def check_time(title:str,logger):
    """ try catch"""
    time1 = time.time()
    yield
    time2 = time.time()
    logger.debug(f"{title}: {time2-time1}")

    

def extra_docs(inputs:str)->dict:
    """ docs """
    pattern1 = r'<context>(.*?)<\/context>'
    pattern2 = r'<source id="(\d+)">(.*?)<\/source>'

    match = re.search(pattern1, inputs,re.DOTALL)

    if match:
        sources = match.group(1).strip()
        matches = re.findall(pattern2, sources)

    result = {int(id): content for id, content in matches}
    return result

class ChatBox():
    """ chatbox """
    def __init__(self) -> None:
        self.bx = BianXieAdapter()
        self.dicts = load_config()
        self.query_persist_dir = self.dicts.get('query_persist_dir')
        self.model_pool = self.dicts.get("ModelCards")
        self.file_path = 'clientz/config.yaml'
        self._last_modified_time = None
        self._update_last_modified_time()
        self.init_lazy_parameter()
        self.query = None

    def _update_last_modified_time(self):
        """更新存储的最后修改时间"""
        try:
            self._last_modified_time = os.path.getmtime(self.file_path)
        except FileNotFoundError:
            self._last_modified_time = None # 文件不存在时设为None

    def check_and_trigger(self):
        """检查文件是否变化，如果变化则触发动作"""
        try:
            current_modified_time = os.path.getmtime(self.file_path)
            if current_modified_time != self._last_modified_time:
                print(f"文件 '{self.file_path}' 已发生变化。")
                self._trigger_action()
                self._last_modified_time = current_modified_time # 更新存储的时间
            else:
                print(f"文件 '{self.file_path}' 未发生变化。")
        except FileNotFoundError:
            print(f"文件 '{self.file_path}' 不存在。")
            self._last_modified_time = None # 文件不存在时重置状态
        except Exception as e:
            print(f"检查文件时发生错误: {e}")

    def _trigger_action(self):
        """当文件发生变化时触发的动作"""
        # 可以修改
        # 这里可以放置你想要执行的具体动作，例如：
        # - 读取文件内容
        # - 处理文件数据
        # - 调用其他函数
        print("触发预定动作...")
        # 示例：读取文件内容并打印
        try:
            self.dicts = load_config()

        except FileNotFoundError:
            print(f"触发动作时文件 '{self.file_path}' 不存在。")
        except Exception as e:
            print(f"读取文件时发生错误: {e}")

    def product(self,prompt_with_history: str, model: str) -> str:
        """ x """
        prompt_with_history, model
        return ''

    def init_lazy_parameter(self):
        """ 一个懒加载的初始化头部 """
        self.chat_with_agent_notes_object = None


    async def astream_product(self,prompt_with_history: str, model: str) -> Any:
        """
        # 只需要修改这里
        """
        self.check_and_trigger()
        prompt_no_history = extract_last_user_input(prompt_with_history)
        logger.debug(f"# prompt_no_history : {prompt_no_history}")
        logger.debug(f"# prompt_with_history : {prompt_with_history}")
        ## __init__ ##

        if model[4:] in self.model_pool:
            self.bx.set_model(model[4:])
            for word in self.bx.product_stream(prompt_with_history):
                yield word

        elif model == "config_info":
            logger.info(f"running {model}")
            yield f"query_dir: {self.query_persist_dir}, dicts {str(self.dicts)}"

            if self.chat_with_agent_notes_object:
                yield self.chat_with_agent_notes_object.tool_calls()
        elif model == "long_memory_v2_retriver":
            if not self.query:
                director = Director(BuilderFactory(BuilderType.CHAT_HISTORY_MEMORY_BUILDER))
                self.query = director.construct()
            if len(prompt_with_history.split('\n')) == 1:
                self.query.reload()

            relevant_memories = self.query.retrieve_search(prompt_no_history)
            memories_str = '\n'.join([i.metadata.get('docs') for i in relevant_memories])
            yield memories_str

        elif model == 'chat_with_long_memory_v2':
            """
            # 电脑 内存就是对应chat_history
            # 硬盘 + 内置硬盘 其实就是 大模型潜意识与知识库维度
            # 还要再加一些 寄存器的方式
            """
            logger.info(f"running {model}")

            self.bx.set_model("gemini-2.5-flash-preview-04-17-nothinking")
            system_prompt = ""
            if not self.query:
                director = Director(BuilderFactory(BuilderType.CHAT_HISTORY_MEMORY_BUILDER))
                self.query = director.construct()
            if len(prompt_with_history.split('\n')) == 1:
                self.query.reload()

            if prompt_no_history == "上传记忆":
                self.query.update(prompt_with_history)
                yield '上传完成'
            elif prompt_no_history.startswith('上传文章'):
                context = f"user: {prompt_no_history}\nassistant: 上传完成"
                print(context,'contextxxxxxxxx')
                self.query.update(context)
                yield '上传完成'
            else:
                with check_time("retriver_search_time",logger = logger):
                    relevant_memories = self.query.retrieve_search(prompt_no_history)
                with check_time("拼接内容",logger = logger):
                    memories_str = '\n'.join([i.metadata.get('docs') for i in relevant_memories])

                    prompt = system_prompt +"\n"+ memories_str +"\n"+prompt_with_history
                time1 = time.time()
                for word in self.bx.product_stream(prompt):
                    logger.debug(time.time()-time1)
                    yield word

        elif model == 'Experts_V1':
            logger.info(f"running {model}")

            doc_dict = extra_docs(prompt_with_history)

            if not self.chat_with_agent_notes_object:
                agent = AgentFactory(AgentType.ReactAgent,tools = [take_notes,read_notes])

                agt = EasyAgentz(agent)
                self.chat_with_agent_notes_object = agt

            result = await self.chat_with_agent_notes_object.run(prompt_no_history)
            yield result


        elif model == 'chat_with_Agent_notes':
            logger.info(f"running {model}")

            def take_notes(text: str) -> None:
                """Some important contents can be recorded"""
                with open('notes.txt','a',encoding="utf-8") as f:
                    f.write(text)

            def read_notes() -> str:
                """Read the important contents that were once recorded"""
                with open('notes.txt','r',encoding="utf-8") as f:
                    text = f.read()
                return text

            if not self.chat_with_agent_notes_object:
                agent = AgentFactory(AgentType.ReactAgent,tools = [take_notes,read_notes])

                agt = EasyAgentz(agent)
                self.chat_with_agent_notes_object = agt

            result = await self.chat_with_agent_notes_object.run(prompt_no_history)
            yield result

        elif model == 'Custom_Agent_Latest':
            logger.info(f"running {model}")


            def take_notes(text: str) -> None:
                """Some important contents can be recorded"""
                with open('notes.txt','a',encoding="utf-8") as f:
                    f.write(text)

            def read_notes() -> str:
                """Read the important contents that were once recorded"""
                with open('notes.txt','r',encoding="utf-8") as f:
                    text = f.read()
                return text

            logger.debug('############# prompt_with_history #############')
            logger.debug(prompt_with_history)
            logger.debug('############# prompt_no_history #############')

            if not self.chat_with_agent_notes_object:
                agent = AgentFactory(AgentType.ReactAgent,tools = [take_notes,read_notes])

                agt = EasyAgentz(agent)
                self.chat_with_agent_notes_object = agt

            result = await self.chat_with_agent_notes_object.run(prompt_no_history)
            yield result

        else:
            yield 'pass'
