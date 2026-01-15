pragma circom 2.0.0;

include "circomlib/circuits/comparators.circom";

template AgeBalance() {
    // Private inputs
    signal input age;
    signal input balance;

    // Public claim
    signal input valid;

    // Internal signals
    signal age_ok;
    signal balance_ok;

    // age < 18 ?
    component ageCheck = LessThan(8);
    ageCheck.in[0] <== age;
    ageCheck.in[1] <== 18;
    age_ok <== 1 - ageCheck.out;

    // balance < 1000 ?
    component balanceCheck = LessThan(32);
    balanceCheck.in[0] <== balance;
    balanceCheck.in[1] <== 1000;
    balance_ok <== 1 - balanceCheck.out;

    // Enforce the claim
    valid === age_ok * balance_ok;
}

component main { public [valid] } = AgeBalance();
