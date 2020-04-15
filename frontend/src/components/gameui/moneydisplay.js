import React from "react"
import * as gamestate from "../../gamestate"

const MoneyDisplay = (props) => {
  const actions = props.actions

  return <div style={{ display: "inline-block", marginLeft: "5px" }}>
    <h3 style={{ display: "inline-block", marginBottom: "5px" }}>${gamestate.moneyForPlayer(actions, props.playerId)}M</h3>
  </div>
}

export default MoneyDisplay