import chivel

# set cwd to the directory containing this file
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

for i in range(chivel.DISPLAY_COUNT):
	screen = chivel.capture(i)
	matches = chivel.find(screen, ".*File.*")
	if matches:
		for match in matches:
			chivel.mouse_move(i, match)
			chivel.wait(0.5)
			chivel.mouse_click()
			chivel.wait(0.5)
	else:
		print(f"No matches found on display {i}")