import datetime
import random


def getTimeStamp(messagedate):
	now = datetime.datetime.now()
	timeElapsed = now - messagedate
	if timeElapsed > datetime.timedelta(days=3):
		return "%s/%s/%s at %s:%s" % (messagedate.month, messagedate.day, messagedate.year, messagedate.hour, messagedate.minute)
	elif timeElapsed > datetime.timedelta(days=1):
		return str(int(datetime.timedelta.total_seconds(timeElapsed) // 86400)) + " Days Ago"
	elif timeElapsed > datetime.timedelta(hours=1):
		return str(int(datetime.timedelta.total_seconds(timeElapsed) // 3600)) + " Hours Ago"
	elif timeElapsed > datetime.timedelta(minutes=1):
		return str(int(datetime.timedelta.total_seconds(timeElapsed) // 60)) + " Minutes Ago"
	else:
		return "Just Now"

def getRandomName():
	adjs = [
    "autumn", "hidden", "bitter", "misty", "silent", "empty", "dry", "dark",
    "summer", "icy", "delicate", "quiet", "white", "cool", "spring", "winter",
    "patient", "twilight", "dawn", "crimson", "wispy", "weathered", "blue",
    "billowing", "broken", "cold", "damp", "falling", "frosty", "green",
    "long", "late", "lingering", "bold", "little", "morning", "muddy", "old",
    "red", "rough", "still", "small", "sparkling", "throbbing", "shy",
    "wandering", "withered", "wild", "black", "young", "holy", "solitary",
    "fragrant", "aged", "snowy", "proud", "floral", "restless", "divine",
    "polished", "ancient", "purple", "lively", "nameless"
  	]
  	nouns = [
    "waterfall", "river", "breeze", "moon", "rain", "wind", "sea", "morning",
    "snow", "lake", "sunset", "pine", "shadow", "leaf", "dawn", "glitter",
    "forest", "hill", "cloud", "meadow", "sun", "glade", "bird", "brook",
    "butterfly", "bush", "dew", "dust", "field", "fire", "flower", "firefly",
    "feather", "grass", "haze", "mountain", "night", "pond", "darkness",
    "snowflake", "silence", "sound", "sky", "shape", "surf", "thunder",
    "violet", "water", "wildflower", "wave", "water", "resonance", "sun",
    "wood", "dream", "cherry", "tree", "fog", "frost", "voice", "paper",
    "frog", "smoke", "star"
  	]
	animals = ["adelie", "affenpinscher", "hound", "civet", "elephant", "penguin", "ainu", "akbash", "akita", "malamute", "albatross", "alligator", "dachsbracke", "bulldog","foxhound", "angelfish", "ant", "anteater", "antelope", "appenzeller", "fox", "hare", "wolf", "armadillo", "mist", "shepherd", "terrier", "avocet", "axolotl", "baboon", "camel", "badger", "balinese", "bandicoot", "barb", "barnacle", "barracuda", "basenji", "basking", "bat", "beagle", "bear", "collie", "beaver", "beetle", "bichon", "binturong", "bird", "birman", "bison", "rhinoceros", "bloodhound", "bluetick", "bobcat", "bolognese", "bombay", "bongo", "bonobo", "booby", "orangutan", "boykin", "budgerigar", "budgie", "buffalo", "bullfrog", "bumblebee", "burmese", "butterfly", "fish", "caiman", "lizard", "canaan", "capybara", "caracal", "carolina", "cassowary", "cat", "caterpillar", "catfish", "centipede", "cesky", "fousek", "chameleon", "chamois", "cheetah", "chicken", "chihuahua", "chimpanzee", "chinchilla", "chinook", "chinstrap", "chipmunk", "cichlid", "leopard", "clumber", "coati", "cockroach", "coral", "cottontop", "tamarin", "cougar", "cow", "coyote", "crab", "macaque", "crane", "crocodile", "cuscus", "cuttlefish", "dachshund", "dalmatian", "frog", "deer", "bracke", "dhole", "dingo", "discus", "doberman", "pinscher", "dodo", "dog", "dogo", "argentino", "dolphin", "donkey", "dormouse", "dragonfly", "drever", "duck", "dugong", "dunker", "dusky", "eagle", "gorilla", "echidna", "mau", "emu", "falcon", "fennec", "ferret", "flamingo", "flounder", "fly", "fossa", "frigatebird", "gar", "gecko", "gerbil", "gharial", "gibbon", "giraffe", "goat", "oriole", "retriever", "goose", "gopher", "grasshopper", "greyhound", "grouse", "guppy", "hammerhead", "shark", "hamster", "harrier", "havanese", "hedgehog", "heron", "himalayan", "hippopotamus", "horse", "humboldt", "hummingbird", "hyena", "ibis", "iguana", "impala", "indri", "insect", "setter", "wolfhound", "jackal", "jaguar", "chin", "javanese", "jellyfish", "kakapo", "kangaroo", "kingfisher", "kiwi", "koala", "kudu", "labradoodle", "ladybird", "lemming", "lemur", "liger", "lion", "lionfish", "llama", "lobster", "owl", "lynx","macaw", "magpie", "malayancivet", "maltese", "manatee", "mandrill", "markhor", "mastiff", "mayfly", "meerkat", "millipede", "mole", "molly", "mongoose", "mongrel", "monitor", "monkey", "moorhen", "moose", "eel", "moray", "moth", "mouse", "mule", "neanderthal", "neapolitan", "newfoundland", "newt", "nightingale", "numbat", "ocelot", "octopus", "okapi", "olm", "opossum", "ostrich", "otter", "oyster", "pademelon", "panther", "parrot", "peacock", "pekingese", "pelican", "persian", "pheasant", "pig", "pika", "pike", "piranha", "platypus", "pointer", "poodle", "porcupine", "possum", "prawn", "puffin", "pug", "puma", "marmoset", "pygmy","quail", "quetzal", "quokka", "quoll", "rabbit", "raccoon", "ragdoll", "rat", "rattlesnake", "reindeer", "robin", "rockhopper", "rottweiler", "salamander", "saola", "scorpion", "seahorse", "seal", "serval", "sheep", "shrimp", "siamese", "siberian", "skunk", "sloth", "snail", "snake", "snowshoe", "somali", "sparrow", "dogfish", "sponge", "squid", "squirrel", "starfish", "stickbug", "stingray", "stoat", "swan", "tang", "tapir", "tarsier", "termite", "tetra", "tiffany", "tiger", "tortoise", "toucan", "tropicbird", "tuatara", "turkey", "uakari", "uguisu", "umbrellabird", "vulture", "wallaby", "walrus", "warthog", "wasp", "weasel", "whippet", "wildebeest", "wolverine", "wombat", "woodlouse", "woodpecker", "wrasse", "yak", "yorkie", "yorkiepoo", "zebra", "zebu", "zonkey", "zorse"]
	return adjs[random.randint(0, len(adjs)-1)] + " " + animals[random.randint(0, len(animals)-1)]

print getRandomName()
