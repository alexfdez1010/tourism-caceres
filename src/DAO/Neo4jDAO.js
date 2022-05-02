export class Neo4jDAO{
    constructor(url, user, password){
        const neo4j = require('neo4j-driver')
        this.driver = neo4j.driver(url, neo4j.auth.basic(user, password));
    }

    async close(){
        await this.driver.close();
    }

    async getAllNodes(){
        const session = this.driver.session();
        const result = await session.readTransaction(tx => tx.run(`MATCH (n:Node) RETURN n`))
        await session.close()
        return result.records.map(record => record.get('n').properties)
    }

    async searchByType(category){
        const session = this.driver.session();
        let result
        if(category === "Cualquiera"){
            result = await session.readTransaction(tx => tx.run(`MATCH (n:Node) RETURN n`))
        }
        else{
            category = category.toUpperCase()
            let query = `MATCH (n:Node {category : $category}) RETURN n`
            result = await session.readTransaction(tx => tx.run(query, {category: category}))
        }
        await session.close()
        return result.records.map(record => record.get("n").properties);
    }

    async searchByCloseness(name, distance, sameCategory){
        const session = this.driver.session();
        let result
        let query
        let subquery
        if(distance === "Muy cerca"){
            subquery = "r:VERY_CLOSE"
        }
        else{
            subquery = "r:VERY_CLOSE|NEAR"
        }
        if(sameCategory){
            query = "MATCH (n:Node {name : $name})-["+subquery+"]-(m:Node) WHERE n.category = m.category RETURN m"
        }
        else{
            query = "MATCH (n:Node {name : $name})-["+subquery+"]-(m:Node) RETURN m"
        }
        console.log(query)
        result = await session.readTransaction(tx => tx.run(query, {name: name}))
        console.log(result.records)
        await session.close()
        return result.records.map(record => record.get("m").properties);
    }

    async searchByName(name){
        const session = this.driver.session();
        let result = await session.readTransaction(tx => tx.run(`MATCH (n:Node {name : $name}) RETURN n`, {name: name}))
        await session.close()
        return result.records.map(record => record.get("n").properties)[0];
    }
}