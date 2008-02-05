totalPechaPages = 14
div, mod = divmod(totalPechaPages, 4)
if mod == 0:
  totalActualPages = div
else:
  totalActualPages = div + 1

for currentPage in xrange(1, totalPechaPages + 1):
  if currentPage <= totalPechaPages / 2.0:
    firstHalf = True
  else:
    firstHalf = False
  secondHalf = not firstHalf
  if firstHalf:
    currentActualPage = int(currentPage / 2.0 + 0.5)
  else:
    currentActualPage = totalPechaPages - int(currentPage / 2.0 + 0.5) - 3
  if ((firstHalf and (currentPage % 2) == 1) or (secondHalf and (currentPage % 2) == 0)):
    orientation = 'upsidedown'
    side = '2nd'
  else:
    orientation = 'rightsideup'
    side = '1st'
  print currentPage, currentActualPage, side, orientation, firstHalf, secondHalf
