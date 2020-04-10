import React from "react"
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

  const [demandOne, demandTwo, demandThree] = props.demands;
  return (
    <div style={{ display: "inline-block", margin: "5px", backgroundColor: "#ccc" }}>
      <div style={{ display: "inline-block" }}>
        <img width={80} src={goodsIcons[demandOne.good]}/>
        <h4>{goodsNames[demandOne.good].split(":")[0]}</h4>
        <h5>to {demandOne.destination}</h5>
        <h2>$ {demandOne.price}</h2>
        <button onClick={() => {props.removeMe()}}>Complete</button>
      </div>
      <h3 style={{ display: "inline-block", margin: "20px" }}>OR</h3>
      <div style={{ display: "inline-block" }}>
        <img width={80} src={goodsIcons[demandTwo.good]}/>
        <h4>{goodsNames[demandTwo.good].split(":")[0]}</h4>
        <h5>to {demandTwo.destination}</h5>
        <h2>$ {demandTwo.price}</h2>
        <button onClick={() => {props.removeMe()}}>Complete</button>
      </div>
      <h3 style={{ display: "inline-block", margin: "20px" }}>OR</h3>
      <div style={{ display: "inline-block" }}>
        <img width={80} src={goodsIcons[demandThree.good]}/>
        <h4>{goodsNames[demandThree.good].split(":")[0]}</h4>
        <h5>to {demandThree.destination}</h5>
        <h2>$ {demandThree.price}</h2>
        <button onClick={() => {props.removeMe()}}>Complete</button>
      </div>
    </div>
  )
}

export default DemandCard