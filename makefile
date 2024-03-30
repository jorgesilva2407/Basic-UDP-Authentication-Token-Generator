all: itr itv gtr gtv

itr:
	@echo "---------------------------------------Criando SAS de usuários---------------------------------------"
	@./client.py slardar.snes.2advanced.dev 51001 itr user123 123
	@./client.py slardar.snes.2advanced.dev 51001 itr user456 456
	@./client.py slardar.snes.2advanced.dev 51001 itr user789 789

itv:
	@echo "--------------------------------------Validando SAS de usuários--------------------------------------"
	@./client.py slardar.snes.2advanced.dev 51001 itv user123:123:af2c7cef144e202e460ec176097e428abdffb256246964e61fc07a4cb462a4c6
	@./client.py slardar.snes.2advanced.dev 51001 itv user456:456:ee014c4f95491401fe46889abbbdd22222445bb1852ce7103132f9baaa6db435
	@./client.py slardar.snes.2advanced.dev 51001 itv user789:789:506630b7c00d34af879b724de66f66fc56955f41309d9b7c9d8e920e890c8014

gtr:
	@echo "---------------------------------------Criando GAS de usuários---------------------------------------"
	@./client.py slardar.snes.2advanced.dev 51001 gtr 3 user123:123:af2c7cef144e202e460ec176097e428abdffb256246964e61fc07a4cb462a4c6 user456:456:ee014c4f95491401fe46889abbbdd22222445bb1852ce7103132f9baaa6db435 user789:789:506630b7c00d34af879b724de66f66fc56955f41309d9b7c9d8e920e890c8014

gtv:
	@echo "--------------------------------------Validando GAS de usuários--------------------------------------"
	@./client.py slardar.snes.2advanced.dev 51001 gtv user123:123:af2c7cef144e202e460ec176097e428abdffb256246964e61fc07a4cb462a4c6+user456:456:ee014c4f95491401fe46889abbbdd22222445bb1852ce7103132f9baaa6db435+user789:789:506630b7c00d34af879b724de66f66fc56955f41309d9b7c9d8e920e890c8014+3f6bb62185aca1fbbf754e1112885d640f6d2268d6e8f748d3ae79c98117eec0