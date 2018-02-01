""" The main entry point. Invoke as `postgrespy`"""
import click

@click.group()
def cli():
    pass

@click.command()
def makemigrations():
    click.echo('making migrations')

cli.add_command(makemigrations)

def main():
    cli()

if __name__ == '__main__':
    main()


