pragma circom 2.0.0;

include "circomlib/circuits/comparators.circom";

template AgeBalance() {
    // Private inputs
    signal input age;
    signal input balance;

    // Public outputs
    signal output age_ok;
    signal output balance_ok;

    // Check age >= 18
    component ageCheck = LessThan(8);
    ageCheck.in[0] <== age;
    ageCheck.in[1] <== 18;

    // Check balance >= 1000
    component balanceCheck = LessThan(32);
    balanceCheck.in[0] <== balance;
    balanceCheck.in[1] <== 1000;

    // If age < 18, ageCheck.out = 1 → invalid
    age_ok <== 1 - ageCheck.out;

    // If balance < 1000, balanceCheck.out = 1 → invalid
    balance_ok <== 1 - balanceCheck.out;
}

component main = AgeBalance();
