# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mongorepository', 'mongorepository.repositories', 'mongorepository.utils']

package_data = \
{'': ['*']}

install_requires = \
['motor>=3.1.1,<4.0.0', 'polyfactory>=2.21.0,<3.0.0', 'pydantic>=2.11.7,<3.0.0']

setup_kwargs = {
    'name': 'mongorepository',
    'version': '0.6.6',
    'description': '',
    'long_description': '# Mongo Repository\n\nThis package provide a sync and async repositories utilities for mongodb.\n\n## Tutorial\n=======\n\nThe first step is to create a schema inheriting from MongoBaseModel and then create a specialized repository inheriting from Repository or AsyncRepository according to the application.\n\nCreating a db schema\n\n```\nfrom mongorepository.models import MongoBaseModel\n\nclass Person(MongoBaseModel):\n    name: str\n    age: int\n    job: Optional[str]\n\n```\n\nThen create a person repository inheriting from Repository\n\n```\nimport pymongo\nfrom mongorepository.repositories.mongo import Repository\n\ndef get_database(db_name: str):\n    client = pymongo.MongoClient("mongodb://localhost:2707")\n    return client.get_database(db_name)\n\nclass PersonRepository(Repository[Person]):\n    def __init__(self):\n        super().__init__(get_database("my_db_name"))\n\n    class Config:\n        collection = "persons"\n\n```\n\nAnd then:\n\n```\n\nperson = Person(name="John Doe", age=33)\nrepository = PersonRepository()\n\nrepository.save(person)\n\n```\n\nFor async flow use this:\n\n```\nimport asyncio\nfrom motor.motor_asyncio import AsyncIOMotorClient\nfrom mongorepository.repositories.async_mongo import AsyncRepository\n\n\ndef get_database(db_name):\n    client = AsyncIOMotorClient("mongodb://localhost:27017")\n    database = client.get_database(db_name)\n    database.get_io_loop = asyncio.get_event_loop\n    return database\n\n\nclass PersonRepository(AsyncRepository[Person]):\n\n    def __init__(self):\n        super().__init__(get_database("my_db_name"))\n\n    class Config:\n        collection = "persons"\n\n\nperson = Person(name="John Doe", age=33)\nrepository = PersonRepository()\n\nasyncio.run(repository.save(person))\n```\n\n',
    'author': 'Ramon Rodrigues',
    'author_email': 'ramon.srodrigues01@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
