---- MODULE Peterson ----
EXTENDS Naturals, TLC

(*
  Minimal TLA+ model for Peterson's mutual exclusion algorithm (2 processes).
  Intended for TLC model checking (safety: mutual exclusion).
*)

Proc == {0, 1}
Other(p) == 1 - p

VARIABLES flag, turn, pc

TypeOK ==
  /\ flag \in [Proc -> BOOLEAN]
  /\ turn \in Proc
  /\ pc \in [Proc -> {"start", "setturn", "wait", "cs", "exit"}]

Init ==
  /\ flag = [p \in Proc |-> FALSE]
  /\ turn = 0
  /\ pc = [p \in Proc |-> "start"]

Start(p) ==
  /\ pc[p] = "start"
  /\ flag' = [flag EXCEPT ![p] = TRUE]
  /\ pc' = [pc EXCEPT ![p] = "setturn"]
  /\ UNCHANGED turn

SetTurn(p) ==
  /\ pc[p] = "setturn"
  /\ turn' = Other(p)
  /\ pc' = [pc EXCEPT ![p] = "wait"]
  /\ UNCHANGED flag

Wait(p) ==
  /\ pc[p] = "wait"
  /\ ~(flag[Other(p)] /\ turn = Other(p))
  /\ pc' = [pc EXCEPT ![p] = "cs"]
  /\ UNCHANGED <<flag, turn>>

ExitCS(p) ==
  /\ pc[p] = "cs"
  /\ pc' = [pc EXCEPT ![p] = "exit"]
  /\ UNCHANGED <<flag, turn>>

Release(p) ==
  /\ pc[p] = "exit"
  /\ flag' = [flag EXCEPT ![p] = FALSE]
  /\ pc' = [pc EXCEPT ![p] = "start"]
  /\ UNCHANGED turn

Step(p) == Start(p) \/ SetTurn(p) \/ Wait(p) \/ ExitCS(p) \/ Release(p)

Next == \E p \in Proc : Step(p)

MutualExclusion == ~(pc[0] = "cs" /\ pc[1] = "cs")

Spec == Init /\ [][Next]_<<flag, turn, pc>>

THEOREM Spec => []MutualExclusion

====

