def doSomething(desk):
	desk["3"] = "no"

def main():
	desk = {};
	desk["1"] = "hello"
	desk["2"] = "goodbye"

	print desk
	doSomething(desk)
	print desk

main()