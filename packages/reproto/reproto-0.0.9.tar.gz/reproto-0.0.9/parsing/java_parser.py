"""
Java文件解析器

从JADX反编译的Java文件中提取Protobuf的newMessageInfo信息
解析字节码字符串和对象数组，为后续的类型解码做准备

Author: AI Assistant
"""

import re
from pathlib import Path
from typing import Optional, Tuple, List

from utils.logger import get_logger


class JavaParser:
    """
    Java文件解析器
    
    专门解析包含Google Protobuf Lite的newMessageInfo调用的Java文件
    提取其中的字节码字符串和对象数组信息
    """
    
    def __init__(self):
        """初始化解析器，编译正则表达式模式"""
        self.logger = get_logger("java_parser")
        
        # 匹配newMessageInfo调用的正则表达式
        # 格式：GeneratedMessageLite.newMessageInfo(DEFAULT_INSTANCE, "字节码", new Object[]{对象数组})
        self.new_message_info_pattern = re.compile(
            r'GeneratedMessageLite\.newMessageInfo\(\s*'
            r'DEFAULT_INSTANCE\s*,\s*'
            r'"([^"]*)",\s*'  # 捕获字节码字符串
            r'new\s+Object\[\]\s*\{([^}]*)\}',  # 捕获对象数组
            re.DOTALL
        )
    
    def parse_java_file(self, java_file_path: Path) -> Tuple[Optional[str], Optional[List[str]]]:
        """
        解析Java文件，提取newMessageInfo中的关键信息
        
        Args:
            java_file_path: Java文件路径
            
        Returns:
            Tuple[字节码字符串, 对象数组] 或 (None, None) 如果解析失败
        """
        try:
            # 读取Java文件内容
            content = java_file_path.read_text(encoding='utf-8')
            
            # 查找newMessageInfo调用
            match = self.new_message_info_pattern.search(content)
            if not match:
                return None, None
            
            # 提取字节码字符串和对象数组字符串
            info_string = match.group(1)
            objects_str = match.group(2)
            
            # 解析对象数组
            objects_array = self._parse_objects_array(objects_str)
            
            return info_string, objects_array
            
        except Exception as e:
            self.logger.error(f"❌ 解析Java文件失败 {java_file_path}: {e}")
            return None, None
    
    def _parse_objects_array(self, objects_str: str) -> List[str]:
        """
        解析Java对象数组字符串
        
        处理复杂的Java对象数组语法，包括：
        - 字符串字面量（带引号）
        - 类引用（如ContactPhone.class）
        - 嵌套的括号和逗号分隔
        
        Args:
            objects_str: 对象数组的字符串表示
            
        Returns:
            解析后的对象列表
        """
        objects = []
        
        # 预处理：清理空白字符
        objects_str = objects_str.strip()
        if not objects_str:
            return objects
        
        # 智能分割：处理嵌套括号和字符串
        parts = self._smart_split(objects_str)
        
        # 后处理：清理和标准化每个对象
        for part in parts:
            cleaned_part = self._clean_object_part(part)
            if cleaned_part:
                objects.append(cleaned_part)
        
        return objects
    
    def _smart_split(self, text: str) -> List[str]:
        """
        智能分割字符串，正确处理嵌套括号和字符串字面量
        
        Args:
            text: 要分割的文本
            
        Returns:
            分割后的部分列表
        """
        parts = []
        current_part = ""
        paren_count = 0
        in_string = False
        escape_next = False
        
        for char in text:
            # 处理转义字符
            if escape_next:
                current_part += char
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                current_part += char
                continue
            
            # 处理字符串字面量
            if char == '"' and not escape_next:
                in_string = not in_string
                current_part += char
                continue
                
            if in_string:
                current_part += char
                continue
            
            # 处理括号嵌套
            if char in '([{':
                paren_count += 1
                current_part += char
            elif char in ')]}':
                paren_count -= 1
                current_part += char
            elif char == ',' and paren_count == 0:
                # 顶层逗号，分割点
                parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char
        
        # 添加最后一部分
        if current_part.strip():
            parts.append(current_part.strip())
        
        return parts
    
    def _clean_object_part(self, part: str) -> Optional[str]:
        """
        清理和标准化对象部分
        
        Args:
            part: 原始对象字符串
            
        Returns:
            清理后的对象字符串，如果无效则返回None
        """
        part = part.strip()
        if not part:
            return None
        
        # 移除字符串字面量的引号
        if part.startswith('"') and part.endswith('"'):
            part = part[1:-1]
        
        # 处理类引用：ContactPhone.class -> ContactPhone
        if part.endswith('.class'):
            part = part[:-6]
        
        return part if part else None
    
    def parse_enum_file(self, java_file_path: Path) -> Optional[List[tuple]]:
        """
        解析Java枚举文件，提取枚举值和数值
        
        Args:
            java_file_path: Java文件路径
            
        Returns:
            枚举值列表 [(name, value), ...] 或 None 如果解析失败
        """
        try:
            # 读取Java文件内容
            content = java_file_path.read_text(encoding='utf-8')
            
            # 检查是否是Protobuf枚举类
            if not self._is_protobuf_enum(content):
                return None
            
            # 提取枚举值
            enum_values = self._extract_enum_values(content)
            
            return enum_values if enum_values else None
            
        except Exception as e:
            self.logger.error(f"❌ 解析枚举文件失败 {java_file_path}: {e}")
            return None
    
    def _is_protobuf_enum(self, content: str) -> bool:
        """
        判断是否是Protobuf枚举类
        
        Args:
            content: Java文件内容
            
        Returns:
            是否为Protobuf枚举
        """
        # 检查关键特征
        return (
            'implements Internal.EnumLite' in content and
            'enum ' in content and
            'forNumber(' in content
        )
    
    def _extract_enum_values(self, content: str) -> List[tuple]:
        """
        从Java枚举类中提取枚举值和数值
        
        Args:
            content: Java文件内容
            
        Returns:
            枚举值列表 [(name, value), ...]
        """
        enum_values = []
        
        # 正则表达式匹配枚举定义
        # 例如：UNKNOWN(0), SUCCESS(1), INTERNAL_ERROR(2)
        enum_pattern = re.compile(r'(\w+)\((\d+)\)')
        
        matches = enum_pattern.findall(content)
        
        for name, value in matches:
            # 跳过UNRECOGNIZED枚举值（通常值为-1）
            if name != 'UNRECOGNIZED':
                enum_values.append((name, int(value)))
        
        # 按数值排序
        enum_values.sort(key=lambda x: x[1])
        
        return enum_values

    def get_raw_field_type(self, java_file_path: Path, field_name_raw: str) -> Optional[str]:
        """
        从Java文件中获取指定字段的原始类型
        
        Args:
            java_file_path: Java文件路径
            field_name_raw: 原始字段名（如 latitude_）
            
        Returns:
            字段的Java原始类型，如果找不到则返回None
        """
        try:
            # 读取Java文件内容
            content = java_file_path.read_text(encoding='utf-8')
            
            # 查找字段声明
            field_type = self._extract_field_type_from_content(content, field_name_raw)
            return field_type
            
        except Exception as e:
            self.logger.debug(f"获取字段类型失败 {java_file_path} - {field_name_raw}: {e}")
            return None
    
    def _extract_field_type_from_content(self, content: str, field_name_raw: str) -> Optional[str]:
        """
        从Java文件内容中提取指定字段的类型
        
        Args:
            content: Java文件内容
            field_name_raw: 原始字段名（如 latitude_）
            
        Returns:
            字段的Java类型，如果找不到则返回None
        """
        # 构建字段声明的正则表达式模式
        # 匹配: private Type fieldName_ = ...;
        # 或: private Type fieldName_;
        
        # 转义字段名中的特殊字符
        escaped_field_name = re.escape(field_name_raw)
        
        # 字段声明模式
        patterns = [
            # 标准字段声明: private Type fieldName_ = value;
            rf'private\s+([^\s]+(?:<[^>]*>)?(?:\[\])?)\s+{escaped_field_name}\s*=',
            # 简单字段声明: private Type fieldName_;
            rf'private\s+([^\s]+(?:<[^>]*>)?(?:\[\])?)\s+{escaped_field_name}\s*;',
            # 其他访问修饰符
            rf'(?:public|protected|package)\s+([^\s]+(?:<[^>]*>)?(?:\[\])?)\s+{escaped_field_name}\s*[=;]',
            # 无访问修饰符
            rf'([^\s]+(?:<[^>]*>)?(?:\[\])?)\s+{escaped_field_name}\s*[=;]',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                field_type = match.group(1).strip()
                
                # 清理类型字符串
                cleaned_type = self._clean_field_type(field_type)
                if cleaned_type:
                    self.logger.debug(f"找到字段类型: {field_name_raw} -> {cleaned_type}")
                    return cleaned_type
        
        self.logger.debug(f"未找到字段类型: {field_name_raw}")
        return None
    
    def _clean_field_type(self, field_type: str) -> Optional[str]:
        """
        清理和标准化字段类型字符串
        
        Args:
            field_type: 原始字段类型字符串
            
        Returns:
            清理后的字段类型，如果无效则返回None
        """
        if not field_type:
            return None
        
        # 移除多余的空白字符
        field_type = field_type.strip()
        
        # 跳过明显不是类型的字符串
        if field_type in ['private', 'public', 'protected', 'static', 'final', 'volatile', 'transient']:
            return None
        
        # 处理泛型类型，保留完整的泛型信息
        # 例如: MapFieldLite<String, Contact> 保持不变
        
        # 处理数组类型
        # 例如: String[] 保持不变
        
        # 处理完全限定类名，提取简单类名
        if '.' in field_type and not field_type.startswith('java.'):
            # 对于非java包的类，保留完整路径以便后续处理
            pass
        
        return field_type

    def extract_field_tags(self, java_file_path: Path) -> Optional[dict]:
        """
        从Java文件中提取字段标签信息
        
        优先从Java源码中直接找到字段名与标签的对应关系，
        而不是依赖常量名的转换推测
        
        Args:
            java_file_path: Java文件路径
            
        Returns:
            字段标签映射 {field_name: tag} 或 None 如果解析失败
        """
        try:
            # 读取Java文件内容
            content = java_file_path.read_text(encoding='utf-8')
            
            # 方法1：直接从源码中找到字段声明和对应的FIELD_NUMBER常量
            field_tags = self._extract_field_tags_from_source(content)
            
            if field_tags:
                return field_tags
            
            # 方法2：如果方法1失败，回退到常量名转换方法
            return self._extract_field_tags_from_constants(content)
            
        except Exception as e:
            self.logger.error(f"❌ 提取字段标签失败 {java_file_path}: {e}")
            return None
    
    def _extract_field_tags_from_source(self, content: str) -> Optional[dict]:
        """
        直接从Java源码中提取字段名和标签的对应关系
        
        通过分析实际的字段声明和常量定义来建立准确的映射
        
        Args:
            content: Java文件内容
            
        Returns:
            字段标签映射 {field_name: tag} 或 None
        """
        # 提取所有字段声明
        field_declarations = self._extract_all_field_declarations(content)
        
        # 提取所有FIELD_NUMBER常量
        field_constants = self._extract_field_number_constants(content)
        
        if not field_declarations or not field_constants:
            return None
        
        # 建立字段名到标签的映射
        field_tags = {}
        
        # 尝试通过字段名匹配找到对应的常量
        for field_name in field_declarations:
            # 生成可能的常量名
            possible_const_names = self._generate_possible_constant_names(field_name)
            
            # 查找匹配的常量
            for const_name in possible_const_names:
                if const_name in field_constants:
                    field_tags[field_name] = field_constants[const_name]
                    self.logger.debug(f"    🎯 直接匹配字段: {field_name} -> {const_name} = {field_constants[const_name]}")
                    break
        
        return field_tags if field_tags else None
    
    def _extract_all_field_declarations(self, content: str) -> List[str]:
        """
        提取所有字段声明
        
        Args:
            content: Java文件内容
            
        Returns:
            字段名列表
        """
        field_pattern = re.compile(
            r'private\s+(?:static\s+)?(?:final\s+)?'  # 访问修饰符
            r'[^\s]+(?:<[^>]*>)?(?:\[\])?'             # 类型（包括泛型和数组）
            r'\s+([a-zA-Z_][a-zA-Z0-9_]*_?)\s*[=;]',  # 字段名
            re.MULTILINE
        )
        
        field_names = []
        for match in field_pattern.finditer(content):
            field_name = match.group(1)
            # 跳过明显的常量字段（全大写）
            if not field_name.isupper() and not field_name.startswith('DEFAULT_'):
                field_names.append(field_name)
        
        return field_names
    
    def _extract_field_number_constants(self, content: str) -> dict:
        """
        提取所有FIELD_NUMBER常量
        
        Args:
            content: Java文件内容
            
        Returns:
            常量名到值的映射 {const_name: value}
        """
        field_tag_pattern = re.compile(
            r'\s*public\s+static\s+final\s+int\s+'  # 允许行首有空白字符
            r'([A-Z0-9_]+)_FIELD_NUMBER\s*=\s*(\d+)\s*;'  # 允许常量名包含数字
        )
        
        constants = {}
        for match in field_tag_pattern.finditer(content):
            const_name = match.group(1)
            tag_value = int(match.group(2))
            constants[const_name] = tag_value
        
        return constants
    
    def _generate_possible_constant_names(self, field_name: str) -> List[str]:
        """
        根据字段名生成可能的常量名
        
        Args:
            field_name: 字段名（如 e164Format_, telType_）
            
        Returns:
            可能的常量名列表
        """
        # 移除末尾的下划线
        clean_name = field_name.rstrip('_')
        
        possible_names = []
        
        # 方法1：直接转换为大写
        # e164Format -> E164FORMAT
        possible_names.append(clean_name.upper())
        
        # 方法2：在camelCase边界添加下划线
        # e164Format -> E164_FORMAT
        camel_to_snake = re.sub('([a-z0-9])([A-Z])', r'\1_\2', clean_name).upper()
        possible_names.append(camel_to_snake)
        
        # 方法3：处理数字和字母的边界
        # e164Format -> E_164_FORMAT
        with_number_boundaries = re.sub('([a-zA-Z])([0-9])', r'\1_\2', clean_name)
        with_number_boundaries = re.sub('([0-9])([a-zA-Z])', r'\1_\2', with_number_boundaries)
        with_number_boundaries = re.sub('([a-z])([A-Z])', r'\1_\2', with_number_boundaries).upper()
        possible_names.append(with_number_boundaries)
        
        return list(set(possible_names))  # 去重
    
    def _extract_field_tags_from_constants(self, content: str) -> Optional[dict]:
        """
        从常量定义中提取字段标签（回退方法）
        
        Args:
            content: Java文件内容
            
        Returns:
            字段标签映射 {field_name: tag} 或 None
        """
        # 匹配字段标签常量定义
        field_tag_pattern = re.compile(
            r'\s*public\s+static\s+final\s+int\s+'  # 允许行首有空白字符
            r'([A-Z0-9_]+)_FIELD_NUMBER\s*=\s*(\d+)\s*;'  # 允许常量名包含数字
        )
        
        field_tags = {}
        
        # 查找所有字段标签定义
        for match in field_tag_pattern.finditer(content):
            field_const_name = match.group(1)  # 如 TEXT, ISFINAL
            tag_value = int(match.group(2))     # 如 1, 2
            
            # 转换常量名为字段名
            field_name = self._const_name_to_field_name(field_const_name)
            field_tags[field_name] = tag_value
            
            self.logger.debug(f"    🔄 回退转换字段标签: {field_name} = {tag_value}")
        
        return field_tags if field_tags else None
    
    def _const_name_to_field_name(self, const_name: str) -> str:
        """
        将常量名转换为字段名（通用算法，无硬编码）
        
        Args:
            const_name: 常量名（如 TEXT, ISFINAL, PAYLOADTYPE, E164_FORMAT）
            
        Returns:
            字段名（如 text_, isFinal_, payloadType_, e164Format_）
        """
        # 通用转换算法：将UPPER_CASE转换为camelCase
        if '_' in const_name:
            # 处理下划线分隔的常量名：E164_FORMAT -> e164Format
            parts = const_name.lower().split('_')
            field_name = parts[0] + ''.join(word.capitalize() for word in parts[1:])
        else:
            # 处理单个单词的常量名：TEXT -> text
            # 处理复合词常量名：ISFINAL -> isFinal, PAYLOADTYPE -> payloadType
            field_name = self._split_compound_word(const_name)
        
        return field_name + '_'
    
    def _split_compound_word(self, word: str) -> str:
        """
        智能分割复合词并转换为camelCase
        
        Args:
            word: 大写复合词（如 ISFINAL, PAYLOADTYPE, USERID）
            
        Returns:
            camelCase格式的字段名（如 isFinal, payloadType, userId）
        """
        # 将单词转换为小写
        word_lower = word.lower()
        
        # 使用启发式规则分割复合词
        # 这些是常见的英语词汇模式，无需硬编码特定应用的词汇
        common_prefixes = ['is', 'has', 'can', 'should', 'will', 'get', 'set']
        common_suffixes = ['type', 'id', 'code', 'number', 'name', 'data', 'info', 'status', 'mode', 'format']
        
        # 检查前缀模式
        for prefix in common_prefixes:
            if word_lower.startswith(prefix) and len(word_lower) > len(prefix):
                rest = word_lower[len(prefix):]
                return prefix + rest.capitalize()
        
        # 检查后缀模式
        for suffix in common_suffixes:
            if word_lower.endswith(suffix) and len(word_lower) > len(suffix):
                prefix_part = word_lower[:-len(suffix)]
                return prefix_part + suffix.capitalize()
        
        # 如果没有匹配的模式，尝试基于常见的英语单词边界进行分割
        # 这里可以使用更复杂的NLP技术，但为了保持简单，使用基本的启发式
        
        # 检查常见的双词组合模式
        if len(word_lower) >= 6:
            # 尝试在中间位置分割
            mid_point = len(word_lower) // 2
            for i in range(max(3, mid_point - 2), min(len(word_lower) - 2, mid_point + 3)):
                first_part = word_lower[:i]
                second_part = word_lower[i:]
                
                # 检查是否是合理的分割（基于常见英语单词长度）
                if (3 <= len(first_part) <= 8 and 3 <= len(second_part) <= 8 and
                    not first_part.endswith(second_part[:2]) and  # 避免重复
                    not second_part.startswith(first_part[-2:])):  # 避免重复
                    return first_part + second_part.capitalize()
        
        # 如果无法智能分割，直接返回小写形式
        return word_lower 