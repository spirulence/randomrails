import React from "react"
import { graphql, useStaticQuery } from "gatsby"
import { default as moji } from "../openmoji"
import { gridToBoardPixelX, gridToBoardPixelY } from "./common"
import { ofType, types } from "../../gamestate"


const GoodsLayer = (props) => {
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

  const goodsElements = []

  ofType(props.actions, types.ADD_MAJOR_CITY).forEach(action => {
    const [x, y] = action.data.location
    action.data.available_goods.map((good, goodIndex) => {
      goodsElements.push(<image key={`${action.sequenceNumber}-${goodIndex}`} x={gridToBoardPixelX(x - 1 + goodIndex, y - 1)}
                                y={gridToBoardPixelY(x - 1 + goodIndex, y - 1) - 5}
                                width={40} height={40}
                                href={goodsIcons[good]}/>)
    })
  })

  ofType(props.actions, types.ADD_MEDIUM_CITY).forEach(action => {
    const [x, y] = action.data.location
    action.data.available_goods.map((good, goodIndex) => {
      goodsElements.push(<image key={`${action.sequenceNumber}-${goodIndex}`} x={gridToBoardPixelX(x - 1 + goodIndex, y - 1)}
                                y={gridToBoardPixelY(x - 1 + goodIndex, y - 1) - 5}
                                width={40} height={40}
                                href={goodsIcons[good]}/>)
    })
  })

  ofType(props.actions, types.ADD_SMALL_CITY).forEach(action => {
    const [x, y] = action.data.location
    action.data.available_goods.map((good, goodIndex) => {
      goodsElements.push(<image key={`${action.sequenceNumber}-${goodIndex}`} x={gridToBoardPixelX(x - 1 + goodIndex, y - 1)}
                                y={gridToBoardPixelY(x - 1 + goodIndex, y - 1) - 5}
                                width={40} height={40}
                                href={goodsIcons[good]}/>)
    })
  })

  return (
    <g>
      {goodsElements}
    </g>
  )
}

export default GoodsLayer