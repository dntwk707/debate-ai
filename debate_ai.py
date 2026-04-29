import os
import sys
import click
from dotenv import load_dotenv
from typing import Optional
import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.rule import Rule
from rich.text import Text

load_dotenv()

console = Console()

MODEL = "claude-sonnet-4-6"


def get_ai_side(user_side: str) -> str:
    if user_side not in ("찬성", "반대"):
        raise ValueError(f"유효하지 않은 입장입니다: {user_side!r}")
    return "반대" if user_side == "찬성" else "찬성"


def build_debate_system_prompt(topic: str, ai_side: str) -> str:
    return (
        f'당신은 "{topic}"에 대해 {ai_side} 입장을 가진 전문 토론자입니다.\n'
        "규칙:\n"
        "- 반드시 자신의 입장을 일관되게 유지하세요. 절대 입장을 바꾸지 마세요.\n"
        "- 논리적 근거와 구체적 예시를 들어 주장하세요.\n"
        "- 상대방의 발언 약점을 정확히 지적하고 반박하세요.\n"
        "- 각 발언은 3~4문장으로 간결하고 명확하게 작성하세요.\n"
        "- 존댓말을 사용하고, 토론 형식을 유지하세요."
    )


def build_judge_system_prompt() -> str:
    return (
        "당신은 공정하고 객관적인 토론 심판입니다.\n"
        "아래 토론 내용을 분석하여 다음 형식으로 평가하세요:\n\n"
        "1. 찬성 측 평가: 강점과 약점\n"
        "2. 반대 측 평가: 강점과 약점\n"
        "3. 최종 판정: 더 설득력 있는 측과 그 이유\n\n"
        "공정하게 논리의 질, 근거의 타당성, 반론의 효과성을 기준으로 평가하세요."
    )


def stream_ai_response(client: anthropic.Anthropic, messages: list, system: str) -> str:
    full_response = ""
    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=1024,
            system=system,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                console.print(text, end="", highlight=False)
                full_response += text
        console.print()
    except anthropic.APIStatusError as e:
        console.print(f"\n[bold red]API 오류:[/bold red] {e.message}")
        sys.exit(1)
    except anthropic.APIConnectionError:
        console.print("\n[bold red]연결 오류:[/bold red] API 서버에 연결할 수 없습니다.")
        sys.exit(1)
    return full_response


def print_header(topic: str, user_side: str, ai_side: str, rounds: int):
    header = Text()
    header.append(f"  토론 주제: {topic}\n", style="bold white")
    header.append(f"  당신: {user_side}  |  AI: {ai_side}  |  라운드: {rounds}회", style="cyan")
    console.print(Panel(header, style="bold blue", padding=(0, 1)))
    console.print()


def print_round_banner(current: int, total: int):
    console.print(Rule(f"[bold yellow] 라운드 {current} / {total} [/bold yellow]"))
    console.print()


def get_user_input(user_side: str) -> str:
    while True:
        console.print()
        user_input = Prompt.ask(f"[bold green]당신의 주장 ({user_side})[/bold green]").strip()
        console.print()
        if user_input:
            return user_input
        console.print("[yellow]발언을 입력해주세요.[/yellow]")


def run_debate(
    client: anthropic.Anthropic, topic: str, user_side: str, rounds: int
) -> tuple[list, str, list[tuple[str, str]]]:
    ai_side = get_ai_side(user_side)
    system_prompt = build_debate_system_prompt(topic, ai_side)
    messages: list = []
    debate_log: list[tuple[str, str]] = []  # (speaker_label, content)

    print_header(topic, user_side, ai_side, rounds)

    for round_num in range(1, rounds + 1):
        print_round_banner(round_num, rounds)

        if round_num == 1:
            messages.append({
                "role": "user",
                "content": f'토론을 시작합니다. 주제는 "{topic}"입니다. {ai_side} 입장에서 첫 번째 주장을 펼쳐주세요.',
            })

        console.print(Panel(
            f"[bold red]AI ({ai_side})[/bold red]",
            expand=False,
            border_style="red",
        ))
        ai_response = stream_ai_response(client, messages, system_prompt)
        messages.append({"role": "assistant", "content": ai_response})
        debate_log.append((f"AI({ai_side})", ai_response))

        user_input = get_user_input(user_side)
        debate_log.append((f"사용자({user_side})", user_input))

        messages.append({
            "role": "user",
            "content": f'상대방({user_side} 측)의 주장: {user_input}\n\n이에 대해 반박하고 {ai_side} 입장을 강화하세요.',
        })

    # Final AI closing statement
    console.print(Rule("[bold yellow] 최종 발언 [/bold yellow]"))
    console.print()
    console.print(Panel(
        f"[bold red]AI ({ai_side}) — 최종 발언[/bold red]",
        expand=False,
        border_style="red",
    ))
    messages.append({
        "role": "user",
        "content": f"토론이 끝났습니다. {ai_side} 입장에서 마지막으로 핵심 주장을 요약해주세요.",
    })
    final_response = stream_ai_response(client, messages, system_prompt)
    messages.append({"role": "assistant", "content": final_response})
    debate_log.append((f"AI({ai_side}) 최종발언", final_response))

    return messages, ai_side, debate_log


def run_judge(
    client: anthropic.Anthropic,
    debate_log: list[tuple[str, str]],
    topic: str,
    user_side: str,
    ai_side: str,
):
    console.print()
    console.print(Rule("[bold magenta] 심판 판정 [/bold magenta]"))
    console.print()

    log_text = (
        f'토론 주제: "{topic}"\n'
        f'찬성 측: {"사용자" if user_side == "찬성" else "AI"}\n'
        f'반대 측: {"사용자" if user_side == "반대" else "AI"}\n\n'
        "토론 내용:\n"
    )
    for speaker, content in debate_log:
        log_text += f"\n[{speaker}]\n{content}\n"

    judge_messages = [{"role": "user", "content": log_text}]
    judge_system = build_judge_system_prompt()

    console.print(Panel("[bold magenta]심판[/bold magenta]", expand=False, border_style="magenta"))
    stream_ai_response(client, judge_messages, judge_system)


@click.command()
@click.option("--topic", "-t", default=None, help="토론 주제")
@click.option("--side", "-s", type=click.Choice(["찬성", "반대"]), default=None, help="사용자 입장")
@click.option("--rounds", "-r", default=3, show_default=True, type=click.IntRange(min=1, max=10), help="토론 라운드 수 (1~10)")
def main(topic: Optional[str], side: Optional[str], rounds: int):
    """AI와 1:1 토론을 진행합니다."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[bold red]오류:[/bold red] ANTHROPIC_API_KEY가 설정되지 않았습니다.")
        console.print("  1. cp .env.example .env")
        console.print("  2. .env 파일에 API 키를 입력하세요.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    console.print()
    console.print(Panel(
        "[bold cyan]토론 AI[/bold cyan]\nClaude와 1:1 토론을 시작합니다.",
        border_style="cyan",
        padding=(0, 2),
    ))
    console.print()

    if not topic:
        topic = Prompt.ask("[bold]토론 주제를 입력하세요[/bold]")
    if not side:
        side = Prompt.ask(
            "[bold]당신의 입장을 선택하세요[/bold]",
            choices=["찬성", "반대"],
            default="찬성",
        )

    console.print()

    messages, ai_side, debate_log = run_debate(client, topic, side, rounds)
    run_judge(client, debate_log, topic, side, ai_side)

    console.print()
    console.print(Rule("[bold cyan] 토론 종료 [/bold cyan]"))
    console.print()


if __name__ == "__main__":
    main()
