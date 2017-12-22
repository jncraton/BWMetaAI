-- AISCRIPT.BIN EUD Start = 0x0068C104 / 4 = 264040

-- TMCx Relative Offeset = 864A
-- ZMCx Relative Offset = 99C4 
-- PMCx Relative Offset = A616

-- ZMCx absolute offset = 0x99C4 / 4 = 2671 + 264040 = 266711

-- script start: 0x032b32 start_town, transports_off, farms_notiming

-- ZMCx start: 03 2B 32 3C CD 99 00 93 A2 4B

-- 4 stops: 0x24242424 = 606348324



---- Copy AISCRIPT.BIN pointer to Current Player dividing pointer by 4 during copy

--- Copy 0x0068C104-> Terran Marine Deaths

-- Add each bit to Marine and Firebat deaths
-- Note that the original pointer value is modified here
for i = 30, 0, -1 do
   Trigger {
       players = {P1},
       conditions = {
           Memory(0x0068C104, AtLeast, 2^i);
       },
       actions = {
           SetMemory(0x0068C104, Subtract, 2^i);
           SetDeaths(P1, Add, 2^i, "Terran Marine");
           SetDeaths(P1, Add, 2^i, "Terran Firebat");
           PreserveTrigger();
       }
   }
end

-- Use Firebat deaths to put the original pointer value back
for i = 30, 0, -1 do
   Trigger {
       players = {P1},
       conditions = {
           Deaths(P1, AtLeast, 2^i, "Terran Firebat");
       },
       actions = {
           SetMemory(0x0068C104, Add, 2^i);
           SetDeaths(P1, Subtract, 2^i, "Terran Firebat");
           PreserveTrigger();
       }
   }
end

-- Set 0x6509B0 to EPD(0)

Trigger {
   players={P1},
   actions={
       SetMemory(0x6509B0, SetTo, EPD(0));
       PreserveTrigger();
   }
}

-- Add AISCRIPT.BIN pointer value divided by 4

for i = 30, 2, -1 do
   Trigger {
       players = {P1},
       conditions = {
           Deaths(P1, AtLeast, 2^i, "Terran Marine");
       },
       actions = {
           SetMemory(0x6509B0, Add, 2^(i-2));
           SetDeaths(P1, Subtract, 2^i, "Terran Marine");
           PreserveTrigger();
       }
   }
end

-- Write the new AISCRIPT.BIN 
-- Example:

--Trigger {
--   players={P1},
--   actions={
--       SetMemory(0x6509B0, Add, 0x2671); -- ZMCx offset within AISCRIPT.BIN
--       SetDeaths(CurrentPlayer, SetTo, 0x24131793, 0); -- Stop then magic bytes to find
--       SetMemory(0x6509B0, SetTo, 0); -- Reset Current Player
--       PreserveTrigger();
--   }
--}

{{ write_actions }}

Trigger {
   players={P1},
   actions={
       SetMemory(0x6509B0, SetTo, 0); -- Reset Current Player
       PreserveTrigger();
   }
}

-- Trigger the AI
Trigger {
	players = {P2},
	conditions = {
		Command(CurrentPlayer, AtLeast, 1, "Zerg Hatchery");
	},
	actions = {
		RunAIScriptAt("Zerg Expansion Custom Level", "AI Start 1");
	},
}

Trigger {
	players = {P2},
	conditions = {
		Command(CurrentPlayer, AtLeast, 1, "Protoss Nexus");
	},
	actions = {
		RunAIScriptAt("Protoss Expansion Custom Level", "AI Start 1");
	},
}

Trigger {
	players = {P2},
	conditions = {
		Command(CurrentPlayer, AtLeast, 1, "Terran Command Center");
	},
	actions = {
		RunAIScriptAt("Terran Expansion Custom Level", "AI Start 1");
	},
}

-- No frame delay
--Trigger {
--	players = {P1},
--	conditions = {
--		ElapsedTime(AtLeast, 0);
--	},
--	actions = {
--		SetMemory(0x5124F0, SetTo, 1);
--	},
--}

-- Standard Melee Triggers
Trigger {
	players = {AllPlayers},
	conditions = {
		ElapsedTime(AtLeast, 30);
		Command(CurrentPlayer, AtMost, 0, "Any unit");
	},
	actions = {
		Defeat();
	},
}

Trigger {
	players = {AllPlayers},
	conditions = {
		ElapsedTime(AtLeast, 30);
		Command(NonAlliedVictoryPlayers, AtMost, 0, "Buildings");
	},
	actions = {
		Victory();
	},
}

Trigger {
	players = {AllPlayers},
	conditions = {
		ElapsedTime(AtLeast, 0);
	},
	actions = {
		SetResources(CurrentPlayer, SetTo, 50, Ore);
	},
}