import React, { useEffect, useState } from "react"

const HostingTools = (props) => {
  const [needToFetch, setNeedToFetch] = useState(true)
  const [slots, setSlots] = useState([])
  const [joincodePrefix, setJoincodePrefix] = useState("")
  const gameId = props.gameId;

  useEffect(() => {
    setJoincodePrefix(window.location.protocol + "//" + window.location.host + `/game/${gameId}/join/`)
  },[gameId])

  useEffect(() => {
    if (needToFetch) {
      fetch(`/game/${gameId}/slots/joincodes`).then(
        (response) => {
          return response.json()
        },
      ).then((data) => {
        setSlots(data.result)
        setNeedToFetch(false)
      })
    }
  }, [needToFetch, gameId])

  const slotHtml = slots.map((slot, index) => {
    return <div key={index}>
      <p><div style={{ display: "inline-block", backgroundColor: slot.color, width: "30px", height: "30px", marginRight: "5px" }}/>{joincodePrefix + slot.joincode}</p>
      <p><button onClick={() =>{
        fetch(`/game/${gameId}/actions/adjust-money/player/${slot.playerNumber}/add/1`, {method: "POST"}).then(
          (response) => {
            setNeedToFetch(true)
          },
        )
      }
      }>+$1M</button><button onClick={() =>{
        fetch(`/game/${gameId}/actions/adjust-money/player/${slot.playerNumber}/add/5`, {method: "POST"}).then(
          (response) => {
            setNeedToFetch(true)
          },
        )
      }
      }>+$5M</button><button onClick={() =>{
        fetch(`/game/${gameId}/actions/adjust-money/player/${slot.playerNumber}/add/10`, {method: "POST"}).then(
          (response) => {
            setNeedToFetch(true)
          },
        )
      }
      }>+$10M</button>
        <button onClick={() =>{
          fetch(`/game/${gameId}/actions/adjust-money/player/${slot.playerNumber}/add/50`, {method: "POST"}).then(
            (response) => {
              setNeedToFetch(true)
            },
          )
        }
        }>+$50M</button></p>
    </div>
  });

  return (
    <div style={{display: props.show ? "block": "none"}}>
      <h5>Hosting Tools</h5>
      {slotHtml}
    </div>
  )
}

export default HostingTools