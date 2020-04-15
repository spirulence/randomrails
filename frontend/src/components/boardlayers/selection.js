import { dotRadius, gridToBoardPixelX, gridToBoardPixelY } from "./common"
import React from "react"

const SelectionCircle = (props) => {
  const selected = props.selected

  return (selected !== null ? <g>
    <circle cx={gridToBoardPixelX(selected[0], selected[1])} cy={gridToBoardPixelY(selected[0], selected[1])}
            r={dotRadius * 3} stroke="grey" fill="none"/>
  </g> : <></>)
}

export default SelectionCircle