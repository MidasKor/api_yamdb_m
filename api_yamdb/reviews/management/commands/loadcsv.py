"""Custom manage.py command for loading csv files into project database."""
import csv

from django.core.management.base import BaseCommand, CommandError

from reviews.models import Category, Comment, Genre, GenreTitle, Review, Title
from users.models import User

COMMANDS = {
    "category": Category,
    "comments": Comment,
    "genre": Genre,
    "genre_title": GenreTitle,
    "review": Review,
    "titles": Title,
    "users": User,
}


class Command(BaseCommand):
    help = (
        "The command for loading csv files into projects db."
        " Takes command-line arguments. For example to load"
        "file genre.csv you need to enter the following command:"
        " python manage.py loadcsv review"
        " /home/kubanez/Dev/api_yamdb/api_yamdb/static/data/review.csv."
        " Also you need to load files in order:\n"
        "first - files with models without foreign keys ( genre"
        " category, user, title)\n"
        "then - models with them ( titles, genre_title, review and comment)"
    )

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("command", nargs="+", type=str)
        parser.add_argument("filename", nargs="+", type=str)

    def handle(self, *args, **options):
        command: str = options["command"][0]
        filename: str = options["filename"][0]

        try:
            model = COMMANDS.get(command)
            with open(filename) as f:
                reader = csv.reader(f)
                field_names = next(reader)

                for row in reader:
                    data_to_insert = dict(zip(field_names, row))
                    special_models = [
                        "titles", "genre_title", "review", "comments"]
                    if command not in special_models:
                        model.objects.create(**data_to_insert)
                    elif command == "titles":
                        model.objects.create(
                            id=data_to_insert.get("id"),
                            name=data_to_insert.get("name"),
                            year=data_to_insert.get("year"),
                            category=Category.objects.get(
                                pk=data_to_insert.get("category")
                            ),
                        )
                    elif command == "genre_title":
                        model.objects.create(
                            id=data_to_insert.get("id"),
                            title_id=Title.objects.get(
                                pk=data_to_insert.get("title_id")
                            ),
                            genre_id=Genre.objects.get(
                                pk=data_to_insert.get("genre_id")
                            ),
                        )
                    elif command == "review":
                        model.objects.create(
                            id=data_to_insert.get("id"),
                            title_id=Title.objects.get(
                                id=data_to_insert.get("title_id")
                            ),
                            text=data_to_insert.get("text"),
                            author=User.objects.get(
                                pk=data_to_insert.get("author")),
                            score=data_to_insert.get("score"),
                            pub_date=data_to_insert.get("pub_date"),
                        )
                    elif command == "comments":
                        model.objects.create(
                            id=data_to_insert.get("id"),
                            review_id=Review.objects.get(
                                id=data_to_insert.get("review_id")
                            ),
                            text=data_to_insert.get("text"),
                            author=User.objects.get(
                                pk=data_to_insert.get("author")),
                            pub_date=data_to_insert.get("pub_date"),
                        )
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully loaded the file "%s"' % filename)
            )
        except IOError:
            raise CommandError("File '%s' does not exist" % filename)
