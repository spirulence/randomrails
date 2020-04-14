const types = {
  MOVE_TRAIN: "move_train"
}

function ofType(actions, type) {
  return actions.filter((action) => action.type === type)
}

export function trainLocations(actions) {
  const locations = {}

  ofType(actions, types.MOVE_TRAIN).forEach((action) => {
    locations[action.data.playerNumber] = action.data.to
  })

  return locations
}