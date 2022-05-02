import logging
from enum import Enum

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable


class TypeRelation(Enum):
    VERY_CLOSE: str = "VERY_CLOSE"
    NEAR: str = "NEAR"

    def __str__(self):
        return str(self.value)


class Node:
    name: str
    category: str
    latitude: float
    longitude: float
    link: int

    def __init__(self, name, category, latitude, longitude, link):
        self.name = name
        self.category = category
        self.latitude = latitude
        self.longitude = longitude
        self.link = link

    def __str__(self):
        return "Node: " + self.name + " " + self.category + " " + str(self.latitude) + " " + str(
            self.longitude) + " " + str(self.link)

    def getCoordinates(self):
        return self.latitude, self.longitude


class TourismDAO:

    def __init__(self, driver: GraphDatabase.driver):
        self.driver = driver

    def add_node(self, node: Node):
        with self.driver.session() as session:
            query = ("CREATE (n:Node {name: $name, latitude: $latitude, "
                     "longitude: $longitude, category: $category, link: $link})"
                     "RETURN n")
            result = session.run(query, name=node.name, latitude=node.latitude, longitude=node.longitude,
                                 category=node.category, link=node.link)
            try:
                return result.single()["n"]
            except ServiceUnavailable as exception:
                logging.error("{query} raised an error: \n {exception}".format(
                    query=query, exception=exception))
                raise

    def add_relationship(self, start_node: Node, end_node: Node, relationship_type: str):
        with self.driver.session() as session:
            query = ("MATCH (a:Node), (b:Node) "
                     "WHERE a.name = $start_node AND b.name = $end_node "
                     f"CREATE (a)-[r: {relationship_type} ]->(b) "
                     "RETURN r")
            result = session.run(query, start_node=start_node.name, end_node=end_node.name)
            try:
                return result.single()["r"]
            except ServiceUnavailable as exception:
                logging.error("{query} raised an error: \n {exception}".format(
                    query=query, exception=exception))
                raise
