from functools import reduce

from neo4j import GraphDatabase
from TourismDAO import TourismDAO, Node, TypeRelation, Sequence
from csv import reader

VERY_CLOSE: float = 0.00043125
NEAR: float = 0.001650

# Distancia euclidea
distance = lambda p1, p2: ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5


def main():
    uri = "neo4j+s://b5b6d44e.databases.neo4j.io"
    user = "neo4j"
    password = open("password.txt").read().strip()
    driver = GraphDatabase.driver(uri, auth=(user, password))
    dao = TourismDAO(driver)
    seq = Sequence(0)
    with open('monuments.csv', newline='') as f:
        monuments = reader(f)
        monuments = list(monuments)
    monuments = list(
        map(lambda x: list(map(lambda y: y.strip(), x)), monuments))  # Elimina espacios en blanco dentro de las cadenas
    monuments = monuments[1:]  # Elimina la primera fila
    monuments = list(map(lambda monument: Node(
        id=seq.next(),
        name=f"{monument[3].title()} {monument[4]}",
        category=monument[3],
        latitude=float(monument[2]),
        longitude=float(monument[1]),
        link=monument[5],
    ), monuments))
    with open("restaurants.csv", newline='') as f:
        restaurants = reader(f)
        restaurants = list(restaurants)
    restaurants = list(
        map(lambda x: list(map(lambda y: y.strip(), x)),
            restaurants))  # Elimina espacios en blanco dentro de las cadenas
    restaurants = restaurants[1:]  # Elimina la primera fila
    restaurants = list(map(lambda y: Node(
        id=seq.next(),
        name=f"Restaurante {y[8]}",
        category="RESTAURANTE",
        latitude=float(y[5]),
        longitude=float(y[3]),
        link=y[1]
    ), restaurants))
    with open('cafe.csv', newline='') as f:
        cafes = reader(f)
        cafes = list(cafes)
    cafes = list(
        map(lambda x: list(map(lambda y: y.strip(), x)), cafes))  # Elimina espacios en blanco dentro de las cadenas
    cafes = cafes[1:]  # Elimina la primera fila
    cafes = list(map(lambda cafe: Node(
        id=seq.next(),
        name=cafe[7],
        category="CAFÉ BAR",
        latitude=float(cafe[5]),
        longitude=float(cafe[3]),
        link=cafe[1],
    ), cafes))
    with open('library.csv', newline='') as f:
        libraries = reader(f)
        libraries = list(libraries)
    libraries = list(
        map(lambda x: list(map(lambda y: y.strip(), x)), libraries))  # Elimina espacios en blanco dentro de las cadenas
    libraries = libraries[1:]  # Elimina la primera fila
    libraries = list(map(lambda library: Node(
        id=seq.next(),
        name=library[6],
        category="BIBLIOTECA",
        latitude=float(library[4]),
        longitude=float(library[3]),
        link=library[1],
    ), libraries))
    with open('museum.csv', newline='') as f:
        museums = reader(f)
        museums = list(museums)
    museums = list(
        map(lambda x: list(map(lambda y: y.strip(), x)), museums))  # Elimina espacios en blanco dentro de las cadenas
    museums = museums[1:]  # Elimina la primera fila
    museums = list(map(lambda museum: Node(
        id=seq.next(),
        name=museum[7],
        category="MUSEO",
        latitude=float(museum[5]),
        longitude=float(museum[4]),
        link=museum[2],
    ), museums))
    data = monuments + restaurants + cafes + libraries + museums
    for node in data:
        dao.add_node(node)
        print(f" Added {node}")
    n = len(data)

    for i in range(n):
        for j in range(i + 1, n):
            p1 = data[i].getCoordinates()
            p2 = data[j].getCoordinates()
            d = distance(p1, p2)
            if d < VERY_CLOSE:
                dao.add_relationship(data[i], data[j], str(TypeRelation.VERY_CLOSE))
                print(f"Relationship very close added between {data[i].name} and {data[j].name}")
            elif d < NEAR:
                dao.add_relationship(data[i], data[j], str(TypeRelation.NEAR))
                print(f"Relationship near added between {data[i].name} and {data[j].name}")

    dao.create_indexes()
    dao.close()
    driver.close()


if __name__ == "__main__":
    main()
