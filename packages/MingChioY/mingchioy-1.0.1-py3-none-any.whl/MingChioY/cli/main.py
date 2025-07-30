# jcy
# 2025/6/28 14:58
import click


@click.group()
def main():
    pass


@main.command()
def hello():
    """Say hello via CLI."""
    print("hello")


if __name__ == "__main__":
    main()
