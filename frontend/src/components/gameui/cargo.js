import React from "react"
import * as gamestate from "../../gamestate"
import { graphql, useStaticQuery } from "gatsby"
import { default as moji } from "../openmoji"
import { trainLocations } from "../../gamestate"
import { citiesAtLocation } from "../../gamestate"

const TrainCargo = (props) => {
  const data = useStaticQuery(graphql`
    query {
      goods:  allFile(filter: {relativeDirectory: {eq: "openmoji/openmoji-svg-black"}}) {
        edges {
          node {
            id
            name
            publicURL
          }
        }
      }
    }
  `)

  const goodsIcons = {}
  data.goods.edges.forEach((edge) => {
    goodsIcons[edge.node.name + ".svg"] = edge.node.publicURL
  })

  const goodsNames = {}
  moji.forEach((emoji) => {
    goodsNames[emoji.hexcode + ".svg"] = emoji.annotation
  })

  const actions = props.actions
  const playerId = props.playerId
  const gameId = props.gameId

  let dumpable = false
  const location = trainLocations(actions)[playerId]
  if(location !== undefined){
    if(citiesAtLocation(actions, location).length > 0){
      dumpable = true
    }
  }

  const goodsIndicators = gamestate.cargoForPlayer(actions, playerId).map((pickup, index) => {
    const good = pickup.good
    return <div key={index} style={{ display: "inline-block", margin: "3px" }}>
      <img style={{ display: "inline-block", margin: "0" }} width={60} src={goodsIcons[good]}/>
      {dumpable ? <button style={{ display: "block" }} onClick={() => {
        fetch(`/game/${gameId}/actions/good/dump/${good}/`, { method: "POST" })
      }
      }>Dump</button> : <></>}
    </div>
  })
  if (goodsIndicators.length === 0) {
    return <></>
  }

  return <div style={{ backgroundColor: "#ddd", display: "inline-block", margin: "5px 5px 5px 0" }}>
    <h4 style={{
      textAlign: "center",
      marginTop: "5px",
      marginBottom: "3px",
    }}>Cargo</h4>
    <div>
      {goodsIndicators}
    </div>
  </div>
}

export default TrainCargo