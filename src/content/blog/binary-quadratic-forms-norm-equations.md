---
title: "Computational Number Theory VI: Binary Quadratic Forms, Class Groups, and Norm Equations"
description: "Primitive binary quadratic forms, discriminants, reduction, ideal-class structure, and norm equations in quadratic fields."
pubDate: "2025-05-24"
updatedDate: '2026-09-13'
topics:
- "Mathematical Foundations"
- "Number Theory"
- "Abstract Algebra"
tags:
- "binary-quadratic-forms"
- "class-groups"
- "quadratic-fields"
- "norm-equations"
- "discriminants"
difficulty: "Advanced"
status: "Reference"
series: "Computational Number Theory"
seriesOrder: 6
sourcePath: "experiments/mathematics/number-theory"
draft: false
---
Binary quadratic forms are an old subject with a surprisingly modern afterlife. They connect representation of integers, ideals in quadratic orders, class groups, complex multiplication, and isogeny computations.

## 1. Binary quadratic forms

A binary quadratic form is
$$
Q(x,y)=ax^2+bxy+cy^2
$$
with discriminant
$$
D=b^2-4ac.
$$

A form is **primitive** if $\gcd(a,b,c)=1$.

For negative $D$, positive-definite forms admit reduction theory, giving finite canonical representatives of equivalence classes.

## 2. Equivalence

Two forms are properly equivalent if one is transformed into the other by a change of variables from $SL_2(\mathbb Z)$.

For fixed discriminant $D$, proper equivalence classes of primitive forms carry a composition law. The resulting finite abelian group is the **form class group**.

## 3. From forms to quadratic orders

For suitable discriminants, form classes correspond to ideal classes in a quadratic order. This is why class groups appear both in elementary-looking forms and in algebraic number theory.

The connection is structural, not merely computational: composition of forms mirrors multiplication of ideal classes.

## 4. Norm equations

In a quadratic field $K=\mathbb Q(\sqrt D)$, the field norm is
$$
N(a+b\sqrt D)=a^2-Db^2
$$
for this basis convention.

A norm equation asks for
$$
N(\alpha)=m.
$$
Such equations generalize Pell-type equations and can be studied using ideals, continued fractions, units, and quadratic forms.

## 5. Prime forms

The uploaded Sage experiment constructs forms whose leading coefficient is a chosen prime. This is related to representing primes by forms of discriminant $D$ and to selecting ideal classes with desired norm properties.

It is important not to confuse “a form with prime leading coefficient” with “a prime element” in a ring; the terminology refers to the representation/class-group setting.

## 6. Cryptographic bridge

Class groups of imaginary quadratic orders underlie historical and modern constructions, and complex multiplication uses quadratic-order arithmetic to build elliptic curves with prescribed endomorphism structure. Those applications come later; the mathematical object is the class group itself.
