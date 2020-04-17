import React from "react"
import * as gamestate from "../../gamestate"
import { gridToBoardPixelX, gridToBoardPixelY, spaceBetween } from "./common"

const HighlightsLayer = (props) => {
  const actions = props.actions
  const highlightGood = props.highlightGood
  const highlightCity = props.highlightCity

  const highlights = []

  if(highlightGood !== null){
    gamestate.goodSuppliers(actions, highlightGood).forEach((location, index) => {
      highlights.push(<circle key={highlightGood + index} cx={gridToBoardPixelX(location.x, location.y)}
                              cy={gridToBoardPixelY(location.x, location.y)} r={spaceBetween * 1.1}
                              style={{ fill: "rgba(0,228,95,0.6)" }}/>)
    })
  }

  if(highlightCity !== null){
    gamestate.cities(actions).filter(action => action.data.name === highlightCity)
      .forEach(cityAction => {
        const [x, y] = cityAction.data.location
        highlights.push(<circle key={highlightCity} cx={gridToBoardPixelX(x, y)}
                                cy={gridToBoardPixelY(x, y)} r={spaceBetween * 1.5}
                                style={{ fill: "rgba(255,222,0,0.6)" }}/>)
      })
  }

  return (<g>
    {highlights}
  </g>)
}

export default HighlightsLayer