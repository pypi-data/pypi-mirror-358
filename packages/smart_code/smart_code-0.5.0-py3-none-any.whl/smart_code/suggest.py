# 定义多语言静态文本
MESSAGES = {
    'zh': {
        'suggestion_prefix': '☛ 优化建议',
        'complexity_prefix': '复杂度',
        'hint_prefix': '提示',
        'suggestion_code_prefix': '💡 建议代码'
    },
    'en': {
        'suggestion_prefix': '☛ Suggestion',
        'complexity_prefix': 'Complexity',
        'hint_prefix': 'Hint',
        'suggestion_code_prefix': '💡 Suggested Code'
    }
}

def format_issue(issue, lang='zh'):
    lang_msgs = MESSAGES.get(lang, MESSAGES['en'])  # 默认回退到英文
    
    parts = [f"[{issue['pattern']}] {issue['description']}"]
    
    if issue.get('suggestion'):
        parts.append(f"{lang_msgs['suggestion_prefix']}：{issue['suggestion']}")

    # 如果有建议代码，则格式化输出
    if issue.get('suggestion_code'):
        parts.append(f"{lang_msgs['suggestion_code_prefix']}：\n```python\n{issue['suggestion_code']}\n```")
    
    if issue.get('complexity'):
        parts.append(f"{lang_msgs['complexity_prefix']}：{issue['complexity']}")
    if issue.get('hint'):
        parts.append(f"{lang_msgs['hint_prefix']}：{issue['hint']}")
        
    return '\n'.join(parts)
