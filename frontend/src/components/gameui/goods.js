import React from "react"
import * as gamestate from "../../gamestate"
import { trainLocations } from "../../gamestate"
import { graphql, useStaticQuery } from "gatsby"
import { default as moji } from "../openmoji"

const PickupGoods = (props) => {
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

  const location = trainLocations(actions)[playerId]

  const goodsAtLocation = location === undefined? [] : gamestate.citiesAtLocation(actions, location).flatMap((cityAction) => {
    return cityAction.data.available_goods || []
  })

  const goods = goodsAtLocation.map((value, index) => <div key={index} style={{ display: "inline-block" }}>
    <img style={{ display: "block", margin: "0 auto 0" }} width={40} src={goodsIcons[value]}/>
    <button style={{ display: "block" }} onClick={() => {
      fetch(`/game/${gameId}/actions/good/pickup/${value}/`, { method: "POST" })
    }}>Pickup
    </button>
  </div>)
  return goods.length === 0 ? <></> :
    <div style={{ backgroundColor: "#ddd", display: "inline-block", margin: "5px" }}>
      <div>
        {goods}
      </div>
    </div>
}

export default PickupGoods