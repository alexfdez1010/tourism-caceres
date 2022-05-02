from neo4j import GraphDatabase
from TourismDAO import TourismDAO, Node, TypeRelation
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
    with open('monuments.csv', newline='') as f:
        monuments = reader(f)
        monuments = list(monuments)
    monuments = list(
        map(lambda x: list(map(lambda y: y.strip(), x)), monuments))  # Elimina espacios en blanco dentro de las cadenas
    monuments = monuments[1:]  # Elimina la primera fila
    monuments = list(map(lambda monument: Node(
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
        map(lambda x: list(map(lambda y: y.strip(), x)), restaurants))  # Elimina espacios en blanco dentro de las cadenas
    restaurants = restaurants[1:]  # Elimina la primera fila
    restaurants = list(map(lambda y: Node(
        name=f"Restaurante {y[8]}",
        category="RESTAURANTE",
        latitude=float(y[5]),
        longitude=float(y[3]),
        link=y[1]
    ), restaurants))
    data = monuments + restaurants
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

    driver.close()


if __name__ == "__main__":
    main()
