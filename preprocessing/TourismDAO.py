import logging
from enum import Enum

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable


class Sequence:
    __init_value: int

    def __init__(self, init_value=0):
        self.__init_value = init_value

    def next(self):
        self.__init_value += 1
        return self.__init_value


class TypeRelation(Enum):
    VERY_CLOSE: str = "VERY_CLOSE"
    NEAR: str = "NEAR"

    def __str__(self):
        return str(self.value)


class Node:
    id: int
    name: str
    category: str
    latitude: float
    longitude: float
    link: int

    def __init__(self, id, name, category, latitude, longitude, link):
        self.id = id
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

    def __hash__(self):
        return self.id


class TourismDAO:

    def __init__(self, driver: GraphDatabase.driver):
        self.driver = driver
        self.session = driver.session()

    def add_node(self, node: Node):
        query = ("CREATE (n:Node {id: $id, name: $name, latitude: $latitude, "
                 "longitude: $longitude, category: $category, link: $link})"
                 "RETURN n")
        result = self.session.run(query, id=node.id, name=node.name, latitude=node.latitude, longitude=node.longitude,
                                  category=node.category, link=node.link)
        try:
            return result.single()["n"]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def add_relationship(self, start_node: Node, end_node: Node, relationship_type: str):
        query = ("MATCH (a:Node), (b:Node) "
                 "WHERE a.id = $start_node AND b.id = $end_node "
                 f"CREATE (a)-[r: {relationship_type} ]->(b) "
                 "RETURN r")
        result = self.session.run(query, start_node=start_node.id, end_node=end_node.id)
        try:
            return result.single()["r"]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def create_indexes(self):
        index_id = "CREATE INDEX ON :Node(id)"
        index_category = "CREATE INDEX ON :Node(category)"
        index_name = "CREATE INDEX ON :Node(name)"
        self.session.run(index_id)
        self.session.run(index_category)
        self.session.run(index_name)

    def close(self):
        self.session.close()
