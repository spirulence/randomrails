import React, { useState } from "react"
import { default as moji } from "./openmoji"
import { graphql, useStaticQuery } from "gatsby"

const DemandCard = (props) => {
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

  function demandList(demand){
    let isFillable = props.card.id in props.fillable && props.fillable[props.card.id].good === demand.good && props.fillable[props.card.id].city === demand.destination
    return (<div style={{ display: "inline-block" }}>
      <img width={80} src={goodsIcons[demand.good]}/>
      <h4>{goodsNames[demand.good].split(":")[0]}</h4>
      <h5>to {demand.destination}</h5>
      <h2>$ {demand.price}</h2>
      { isFillable ? <button onClick={() => {props.fillAction(demand.good)}}>Complete</button> : <></>  }
    </div>)
  }

  return (
    <div style={{ display: "inline-block", margin: "5px", backgroundColor: "#ccc" }}>
      {demandList(props.card.demands[0])}
      <h3 style={{ display: "inline-block", margin: "20px" }}>OR</h3>
      {demandList(props.card.demands[1])}
      <h3 style={{ display: "inline-block", margin: "20px" }}>OR</h3>
      {demandList(props.card.demands[2])}
    </div>
  )
}

export default DemandCard