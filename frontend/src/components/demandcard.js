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
    return (<div style={{ display: "block" }}>
      <div style={{ display: "inline-block" }}>
        <img style={{ margin: 0 }} width={60} src={goodsIcons[demand.good]}/>
        { isFillable ? <button onClick={() => {props.fillAction(demand.good)}}>Complete</button> : <></>  }
      </div>
      <div style={{ display: "inline-block" }}>
        <h6 style={{margin: "5px", fontSize: "12px"}}>{goodsNames[demand.good].split(":")[0]}</h6>
        <h6 style={{margin: "5px", fontSize: "13px"}}>to {demand.destination}</h6>
        <h4 style={{margin: "5px"}}>$ {demand.price}</h4>
      </div>
    </div>)
  }

  return (
    <div style={{ display: "inline-block", margin: "5px", backgroundColor: "#ccc" }}>
      {demandList(props.card.demands[0])}
      <h5 style={{ display: "inline-block", margin: "5px" }}>---OR---</h5>
      {demandList(props.card.demands[1])}
      <h5 style={{ display: "inline-block", margin: "5px" }}>---OR---</h5>
      {demandList(props.card.demands[2])}
    </div>
  )
}

export default DemandCard