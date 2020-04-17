import React from "react"
import DemandCard from "./demandcard"
import * as gamestate from "../../gamestate"

const DemandCards = (props) => {
  const actions = props.actions
  const playerId = props.playerId
  const gameId = props.gameId
  const highlightCity = props.highlightCity
  const setHighlightCity = props.setHighlightCity
  const highlightGood = props.setHighlightGood
  const setHighlightGood = props.setHighlightGood

  const demandCards = gamestate.demandCardsForPlayer(actions, playerId)
  const fillable = gamestate.demandsFillable(actions, playerId)

  return <div style={{ backgroundColor: "#ddd", padding: "5px" }}>
    <h4>Demand Cards <button disabled={highlightGood === null && highlightCity === null} onClick={() =>{setHighlightGood(null); setHighlightCity(null)}}>Clear Highlights</button></h4>
    {demandCards.map((demandCard, index) => {
      return <DemandCard highlightGood={highlightGood} highlightCity={highlightCity} setHighlightCity={setHighlightCity} setHighlightGood={setHighlightGood} key={index} card={demandCard} fillable={fillable} fillAction={(good) => {
          fetch(`/game/${gameId}/actions/good/deliver/${good}/card/${demandCard.id}/`, { method: "POST" })
        }
      }/>
    })}
  </div>
}

export default DemandCards