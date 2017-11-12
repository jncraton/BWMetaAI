sc_path = /media/jncraton/2CFAF2F9FAF2BDE0/games/StarCraft
src = src
config = default

all: mpq

run: patch
	@$(sc_path)/StarCraft.exe -launch

run-wine: patch
	@wine $(sc_path)/StarCraft.exe -launch

patch: mpq
	@echo Overwriting existing patch_rt.mpq
	@cp $(sc_path)/patch_rt.mpq $(sc_path)/patch_rt_bak.mpq
	@cp build/patch_rt.mpq $(sc_path)/patch_rt.mpq

mpq: combined_scripts
	@echo Creating MPQ
	@# This effectively replaces a 64050 byte uncompressed aiscript.bin in a patch_rt.mpq file.
	@# The MPQ was split in half leaving a gap that we can just slot our aiscript.bin into.
	@truncate -s 64050 build/aiscript.bin
	@cat tools/patch_rt_pre.mpq build/aiscript.bin tools/patch_rt_post.mpq > build/patch_rt.mpq

bins: combined_scripts
	@echo Creating script binaries
	@python tools/PyAI.pyw -c -w ../build/combined.pyai ../build/aiscript.bin ../build/bwscript.bin

combined_scripts: terran.pyai zerg.pyai protoss.pyai
	@echo Combining scripts
	@cat build/terran.pyai build/zerg.pyai build/protoss.pyai > build/combined.pyai

%.pyai:
	@echo Building $@
	@cp tools/config_$(config).json tools/config.json
	@node tools/build_ai $(subst .pyai,,$@) build/$@;
	@rm tools/config.json

clean:
	@rm -f build/*.bin
	@rm -f build/*.mpq
	@rm -f build/*.pyai