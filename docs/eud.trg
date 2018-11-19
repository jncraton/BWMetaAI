-- Copy aiscript.bin pointer to Current Player dividing pointer by 4 during copy

-- First, copy aiscript.bin pointer (0x0068C104) to Terran Marine Deaths
-- Add each bit to Marine and Firebat deaths
-- Note that the original pointer value is modified here so we need to put it back later
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

-- Set Current Player (0x006509B0) to EPD(0)

Trigger {
   players={P1},
   actions={
       SetMemory(0x006509B0, SetTo, EPD(0));
       PreserveTrigger();
   }
}

-- Add aiscript.bin pointer (now copied to Terran Marine Deaths) divided by 4

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

-- Our modified current player pointer now allows us to write directly to aiscript.bin
-- Setting Deaths of unit 0 for the current player writes to the first word
-- Adding to the current player offset (0x006509B0) allows us to move to the next word
-- A script can easily replace the following with the approptiate write triggers

{{ write_actions }}

-- Here's an example:

--Trigger {
--   players={P1},
--   actions={
--       SetDeaths(CurrentPlayer, SetTo, 0x00000000, 0); -- zero out the first word
--       SetMemory(0x6509B0, Add, 1); -- move to the second word
--       SetDeaths(CurrentPlayer, SetTo, 0x00000000, 0); -- zero out the second word
--       PreserveTrigger();
--   }
--}

-- Put Current Player back to normal
Trigger {
   players={P1},
   actions={
       SetMemory(0x6509B0, SetTo, 0); -- Reset Current Player
       PreserveTrigger();
   }
}

-- Trigger the AI
-- This assumes that the trigger is running on a map with a location called 'AI Start 1'
-- over player 2's start location, and that player 2 is computer player.
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