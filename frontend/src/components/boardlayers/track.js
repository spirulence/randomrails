import React from "react"
import * as gamestate from "../../gamestate"
import { gridToBoardPixelX, gridToBoardPixelY } from "./common"
import { currentPlayers } from "../../gamestate"

function addTrack(collection, action, colors, dontDraw) {
  const [[x1, y1], [x2, y2]] = [action.data.from, action.data.to]
  if(dontDraw.includes(`${x1},${y1},${x2},${y2}`) || dontDraw.includes(`${x2},${y2},${x1},${y1}`)){
    return
  }

  collection.unshift(<line
    key={action.sequenceNumber}
    x1={gridToBoardPixelX(x1, y1)} y1={gridToBoardPixelY(x1, y1)}
    x2={gridToBoardPixelX(x2, y2)} y2={gridToBoardPixelY(x2, y2)}
    style={{ stroke: colors[action.data.playerId], strokeWidth: 4 }}
  />)
}

const TrackLayer = (props) => {
  const actions = props.actions
  const playerColors = {}
  Object.values(currentPlayers(actions)).forEach((player) => {
    playerColors[player.playerId] = player.color
  })

  const trackSegments = []

  const dontDraw = []

  gamestate.ofType(actions, gamestate.types.ERASE_TRACK).forEach(action => {
    const [[x1, y1], [x2, y2]] = [action.data.from, action.data.to]
    dontDraw.unshift(`${x1},${y1},${x2},${y2}`)
  })

  gamestate.ofType(actions, gamestate.types.ADD_TRACK).forEach(action => {
    addTrack(trackSegments, action, playerColors, dontDraw)
  })


  return (<g>
    {trackSegments}
  </g>)
}

export default TrackLayer
