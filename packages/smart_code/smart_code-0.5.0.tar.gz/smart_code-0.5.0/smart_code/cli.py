import argparse
from smart_code import __version__
from smart_code.analyzer import CodeAnalyzer
from smart_code.suggest import format_issue

def main():
    parser = argparse.ArgumentParser(
        description=f"smart_code {__version__}")
    parser.add_argument('files', nargs='+', help='Python files to analyze')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    parser.add_argument('--codemod', action='store_true', help='Rewrite code in-place using codemods')
    parser.add_argument('--lang', choices=['zh', 'en'], default='en', help='Language for suggestions (zh/en)')

    args = parser.parse_args()
    
    analyzer = CodeAnalyzer(lang=args.lang)
    all_issues = []

    for file in args.files:
        issues = analyzer.analyze_file(file)
        if args.json:
            all_issues.extend(issues)
        else:
            for issue in issues:
                # 输出格式：文件名:行号: 描述... 便于跳转
                print(f'{file}:{issue["lineno"]}: {format_issue(issue, lang=args.lang)}')

    if args.json:
        import json
        print(json.dumps(all_issues, ensure_ascii=False, indent=2))

    if args.codemod:
        from smart_code.codemod import refactor_file
        for file in args.files:
            refactor_file(file)

if __name__ == '__main__':
    main()
