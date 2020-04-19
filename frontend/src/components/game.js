import React, { useEffect, useState } from "react"
import CrayonChooser from "./gameui/crayon"
import base64 from "react-native-base64"
import PlayBoard from "./board"
import * as gameapi from  "../gameapi"
import HostingTools from "./gameui/hostingtools"
import MoneyDisplay from "./gameui/moneydisplay"
import { setMyColor } from "../gameapi"
import DemandCards from "./gameui/demands"
import PickupGoods from "./gameui/goods"
import TrainCargo from "./gameui/cargo"
import TurnIndicator from "./gameui/turnindicator"

const Game = (props) => {
  const gameId = props.gameId

  const [actions, setActions] = useState([]);
  const [myPlayerId, setMyPlayerId] = useState(null);
  const [showHostingTools, setShowHostingTools] = useState(false);
  const [inputMode, setInputMode] = useState("none")
  const [highlightCity, setHighlightCity] = useState(null)
  const [highlightGood, setHighlightGood] = useState(null)

  useEffect(() => {
    gameapi.fetchAllActions(gameId, setActions)
  }, [gameId])

  useEffect(() => {
    gameapi.fetchMyPlayerId(gameId, setMyPlayerId)
  }, [gameId])

  useEffect(() => {
    const interval = setInterval(() => {
      if(actions.length > 0){
        gameapi.fetchSupplementalActions(gameId, actions, setActions)
      }
    }, 300)
    return function() {
      clearInterval(interval)
    }
  }, [gameId, actions])

  return (
    <PlayBoard actions={actions} setNeedToFetch={() => {}} gameId={gameId} inputMode={inputMode} highlightCity={highlightCity} highlightGood={highlightGood}>
      <div style={{ zIndex: 1, position: "relative" }}>
        <HostingTools actions={actions} show={showHostingTools} gameId={gameId}/>
        <div style={{ position: "fixed", bottom: "0%", backgroundColor: "#ddd", padding: "5px" }}>
          <CrayonChooser playerId={myPlayerId} actions={actions} setCrayon={(color) => {setMyColor(gameId, myPlayerId, color)}}/>
          <MoneyDisplay playerId={myPlayerId} actions={actions}/>
          <button style={{display: "inline"}} disabled={inputMode === "none"} onClick={() => {setInputMode("none")}}>None</button>
          <button style={{display: "inline"}} disabled={inputMode === "move_train"} onClick={() => {setInputMode("move_train")}}>Move Train</button>
          <button style={{display: "inline"}} disabled={inputMode === "add_track"} onClick={() => {setInputMode("add_track")}}>Add Track</button>
          <button style={{display: "inline"}} disabled={inputMode === "erase_track"} onClick={() => {setInputMode("erase_track")}}>Erase Track</button>
          <button style={{marginRight: "3px", marginLeft:"3px"}} onClick={() => {setShowHostingTools(!showHostingTools)}}>Toggle Host Tools</button>
          <button style={{display: "inline"}} disabled={inputMode !== "add_track"} onClick={() => {gameapi.undoTrack(gameId)}}>Undo Add Track</button>
        </div>
        <div style={{ position: "fixed", bottom: "60px" }}>
          <TrainCargo actions={actions} playerId={myPlayerId} gameId={gameId}/>
          <PickupGoods actions={actions} playerId={myPlayerId} gameId={gameId}/>
          <DemandCards actions={actions} playerId={myPlayerId} gameId={gameId} highlightCity={highlightCity} highlightGood={highlightGood} setHighlightCity={setHighlightCity} setHighlightGood={setHighlightGood}/>
        </div>
        <div style={{ position: "fixed", bottom: "0", right: "0", backgroundColor: "#ddd", padding: "5px" }}>
          <TurnIndicator actions={actions} playerId={myPlayerId} gameId={gameId}/>
        </div>
      </div>
    </PlayBoard>
  )
}

export default Game