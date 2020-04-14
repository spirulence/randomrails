import React, { useEffect, useState } from "react"

const HostingTools = (props) => {
  const [needToFetch, setNeedToFetch] = useState(true)
  const [slots, setSlots] = useState([])
  const [joincodePrefix, setJoincodePrefix] = useState("")
  const gameId = props.gameId

  useEffect(() => {
    setJoincodePrefix(window.location.protocol + "//" + window.location.host + `/game/${gameId}/join/`)
  }, [gameId])

  useEffect(() => {
    if (needToFetch) {
      fetch(`/game/${gameId}/slots/joincodes/`).then(
        (response) => {
          return response.json()
        },
      ).then((data) => {
        setSlots(data.result)
        setNeedToFetch(false)
      })
    }
  }, [needToFetch, gameId])

  function moneyButtons(slot) {
    return [-50, -10, -5, -1, 1, 5, 10, 50].map((amount) => (<button key={amount} onClick={() => {
      fetch(`/game/${gameId}/actions/adjust-money/player/${slot.playerNumber}/${amount > 0 ? "plus" : "minus"}/${Math.abs(amount)}/`, { method: "POST" }).then(
        (response) => {
          setNeedToFetch(true)
        },
      )
    }
    }>${amount}M</button>))
  }

  const slotHtml = slots.map((slot, index) => {
    return <div key={index}>
      <p>
        <div style={{
          display: "inline-block",
          backgroundColor: slot.color,
          width: "30px",
          height: "30px",
          marginRight: "5px",
        }}/>
        {joincodePrefix + slot.joincode}</p>
      <p>{moneyButtons(slot)}</p>
    </div>
  })

  return (
    <div style={{ display: props.show ? "block" : "none" }}>
      <h5>Hosting Tools</h5>
      {slotHtml}
    </div>
  )
}

export default HostingTools