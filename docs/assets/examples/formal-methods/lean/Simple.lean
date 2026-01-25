-- Minimal Lean example (Chapter 9).
-- The goal is to show how to state and prove a small theorem in a proof assistant.

theorem add_zero (n : Nat) : n + 0 = n := by
  rfl

theorem and_swap (p q : Prop) : p ∧ q -> q ∧ p := by
  intro h
  exact And.intro h.right h.left

