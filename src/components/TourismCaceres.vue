<template>
  <div id="container-nodes">
    <div id="search-nodes">
      <form id ="search-by-category" @submit.prevent="searchByCategory">
        <label for="select-nodes">Categoría</label>
        <select id="select-nodes" v-model="selectedOption">
          <option v-for="category in categories" v-bind:key="category" v-bind:value="category">
            {{ category }}
          </option>
        </select>
        <button type="submit">Buscar</button>
      </form>
      <form id="search-closeness" @submit.prevent="searchWay">
        <label for="name-nodes">Nombre </label>
        <input id="name-nodes" type="text" v-model="nameNode">
        <label for="distance-nodes">Cercanía</label>
        <select id="distance-nodes" v-model="distance">
          <option value="Muy cerca">Muy cerca</option>
          <option value="Cerca">Cerca</option>
        </select>
        <input id="same-category" type="checkbox" v-model="sameCategory">
        <label for="same-category">Misma categoría</label>
        <button type="submit">Buscar</button>
      </form>
      <div id="container-path">
        <input type="checkbox" id="show-path" v-model="showPath">
        <label for="show-path">Mostrar ruta</label>
      </div>
    </div>
    <div id="view-selector">
      <input id="list-view" type="radio" value="Lista" v-model="showList" checked>
      <label for="list-view">Lista</label>
      <input id="map-view" type="radio" value="Mapa" v-model="showList">
      <label for="map-view">Mapa</label>
    </div>
    <div id="nodes-list" v-if="showList==='Lista'">
      <div v-for="node in nodes" v-bind:key="node.id">
        <div class="node-item">
          <h3 class="node-item-name" @click="nameNode=node.name">Nombre: {{ node.name }}</h3>
          <div class="node-item-description">Categoría: {{ node.category}}</div>
          <div v-if="node.link.length > 0" class="node-item-link">Link: <a v-bind:href="node.link">{{ node.name }}</a></div>
          <div class="node-item-coors">Latitud: {{node.latitude}} Longitud: {{node.longitude}}</div>
        </div>
      </div>
    </div>
    <div id="nodes-map" v-else>
      <GoogleMap v-bind:api-key="token" style="width: 100%; height: 100%" :center="center" :zoom="15">
        <Marker v-for="node in nodes" v-bind:key="node.id" :options="{
                  position: {lat: Number(node.latitude), lng: Number(node.longitude), title:node.name},
        }">
          <InfoWindow @click.prevent="nameNode=node.name">
            <div class="node-window">
              <div class="node-item-name">Nombre: {{ node.name }}</div>
              <div class="node-item-description">Categoría: {{ node.category}}</div>
              <div v-if="node.link.length > 0" class="node-item-link">Link: <a v-bind:href="node.link">{{ node.name }}</a></div>
              <div class="node-item-coors">Latitud: {{node.latitude}} Longitud: {{node.longitude}}</div>
            </div>
          </InfoWindow>
        </Marker>
        <Polyline v-if="showPath" :options="optionsPath" />
      </GoogleMap>
    </div>
  </div>
</template>

<script>
import json from '../assets/credentials.json'
import t from '../assets/token.json'
import {Neo4jDAO} from '@/DAO/Neo4jDAO'
import { GoogleMap , Marker, InfoWindow, Polyline } from "vue3-google-map"
import * as TSP from '../utils/TSP'


export default {
  name: 'TourismCaceres',
  NEAR: 0.000825,
  VERY_CLOSE: 0.00043125,
  components: {
    GoogleMap,
    Marker,
    InfoWindow,
    Polyline,
  },
  data (){
    return {
      center: {
        lat: 39.4752,
        lng: -6.372
      },
      token: t.tokenMap,
      dao: null,
      nodes: [],
      showPath: false,
      optionsPath: {
        path: [],
        geodesic: true,
        strokeColor: "#000000",
        strokeOpacity: 1.0,
        strokeWeight: 2,
      },
      optionsCircle:{
        strokeColor: "#000000",
        strokeOpacity: 1.0,
        strokeWeight: 2,
        fillColor: "#000000",
        fillOpacity: 0.35,
        center: {lat: 0, lng: 0},
        radius: (this.distance === 'Cerca') ? this.NEAR : this.VERY_CLOSE
      },
      showList: "Lista",
      sameCategory: false,
      nameNode: '',
      selectedOption: 'Cualquiera',
      distance: 'Muy cerca',
      steps: 1,
      categories: [
        "Cualquiera","Restaurante","Palacio","Ermita",
        "Monumento","Casa","Arco", "Torre", "Concatedral",
        "Iglesia","Convento","Café Bar","Museo","Biblioteca"
      ]
    }
  },
  methods: {
    async searchByCategory(){
      this.dao.searchByType(this.selectedOption).then(nodes => {
        this.nodes = nodes
        this.getPath(Math.floor(Math.random() * this.nodes.length))
      })
    },
    async searchWay(){
      let similarName = await this.getSimilarName(this.nameNode)
      this.nameNode = similarName
      await this.dao.searchByCloseness(similarName,this.distance,this.sameCategory).then(nodes => {
        this.nodes = nodes
      })
      await this.dao.searchByName(similarName).then(node => {
        this.optionsCircle.center = {lat: node.latitude, lng: node.longitude}
        this.nodes.push(node)
      })
      if(this.nodes.length > 1){
        this.getPath(this.nodes.length-1)
      }
      else{
        this.optionsPath.path = []
      }
    },
    editDistance(a,b){
      let dp = Array(a.length+1).fill(0).map(() => Array(b.length+1).fill(0));
      let i,j
      a = a.toLowerCase()
      b = b.toLowerCase()
      for(i = 0; i <= a.length; i++){
        dp[i][0] = i
      }
      for(j = 0; j <= b.length; j++){
        dp[0][j] = j
      }
      for(i = 1; i <= a.length; i++){
        for(j = 1; j <= b.length; j++){
          dp[i][j] = Math.min(dp[i-1][j]+1,dp[i][j-1]+1,dp[i-1][j-1]+(a[i-1]===b[j-1]?0:3))
        }
      }
      return dp[a.length][b.length]
    },
    async getSimilarName(name){
      let min_name = ''
      await this.dao.getAllNodes(this.selectedOption).then(nodes => {
        const names = nodes.map(node => node.name)
        let min_distance = Infinity
        for(let i = 0; i < names.length; i++){
          let distance = this.editDistance(name,names[i].substr(0,name.length))
          if(distance < min_distance){
            min_distance = distance
            min_name = names[i]
          }
        }
      })
      return min_name
    },
    getPath(initial) {
      let n = this.nodes.length
      let matrix = Array(n).fill().map(() => Array(n).fill(0));
      let eulerDist = (a, b) => Math.sqrt(Math.pow(a.x - b.x, 2) + Math.pow(a.y - b.y, 2))
      for (let i = 0; i < n; i++) {
        for (let j = 0; j < n; j++) {
          matrix[i][j] = eulerDist(
              {x: this.nodes[i].latitude, y: this.nodes[i].longitude},
              {x: this.nodes[j].latitude, y: this.nodes[j].longitude}
          )
        }
      }
      let order = TSP.TSP(matrix, initial)
      this.optionsPath.path = order.map(i => {
        return {
          lat: Number(this.nodes[i].latitude),
          lng: Number(this.nodes[i].longitude)
        }
      })
      this.showPath = !this.showPath
      setTimeout(
        () => {
          this.showPath = !this.showPath
        },
        25
      )
    }
  },
  beforeMount() {
    const uri = 'neo4j+s://b5b6d44e.databases.neo4j.io';
    this.dao = new Neo4jDAO(uri, json.user, json.password);
    this.searchByCategory()
  },
  unmounted() {
    this.dao.close()
  }
}
</script>

<style scoped>

#container-nodes{
  font-size: 0.75em;
}

#search-nodes{
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 20px;
  width: 1000px;
  margin: 20px auto;
  border: 2px solid black;
}

#search-by-category, #search-closeness, #view-selector, #container-path{
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

#nodes-list{
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: center;
  flex-basis: 20%;
  margin: 30px auto;
}

.node-item{
  width: 300px;
  height: 300px;
  background: deepskyblue;
  margin: 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-radius: 5%;
  gap: 20px;
  color: white;
}

.node-window{
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

input, select, button{
  -moz-box-sizing:content-box;
  -webkit-box-sizing:content-box;
  box-sizing:content-box;
}

label, input[type=text]{
  display: flex;
  justify-content: center;
  align-items: center;
  border: 2px solid black;
  background: deepskyblue;
  padding: 1px 2px;
  height: 20px;
}

input[type=text]{
  height: 20px;
}

button{
  height: 20px;
  width: 100px;
  background: green;
  color: white;
  border: 2px solid black;
  font-size: 20px;
  font-weight: bold;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 20px;
}

input[type=radio] + label, input[type=checkbox] + label, select{
  width: 80px;
  height: 25px;
  border-radius: 20px;
  background: deepskyblue;
}
select{
  width: 120px;
}
input[type=checkbox] + label{
  width: 150px;
}

input[type=radio]:checked + label, input[type=checkbox]:checked + label{
  box-shadow: 0 0 5px black;
  font-weight: bold;
}

input[type=radio], input[type=checkbox]{
  appearance: none;
  border: transparent;
  width: 0;
  height: 0;
}

#view-selector{
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border: 2px solid black;
  padding: 5px 0;
  width: 500px;
  margin: auto;
}

#nodes-map{
  width: 1000px;
  height: 600px;
  margin: 30px auto;
}
</style>
