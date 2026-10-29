/* Starter content. Add a note here; no database or build step is needed.
   Each section can contain paragraphs, a formula, a list, and a tip.
   Keep IDs unique and URL-friendly: they become shareable #note/ID links. */
window.COMMONPLACE_NOTES = [
  {
    id: 'quadratic-equations',
    title: 'Quadratic equations, made simple.',
    subject: 'mathematics',
    level: 'Class 10',
    minutes: 3,
    summary: 'Two roots, a few reliable methods, and one formula worth getting to know.',
    sections: [
      {
        heading: 'Start with the shape.',
        paragraphs: ['A quadratic equation contains a squared variable, but no higher power. Its standard form is ax² + bx + c = 0, where a, b and c are numbers and a is not zero. If a were zero, the squared term would disappear and the equation would be linear.'],
        formula: 'ax² + bx + c = 0,  a ≠ 0',
        tip: 'Rearrange first. For x² = 5x − 6, subtract 5x and add 6 to get x² − 5x + 6 = 0. Now a = 1, b = −5 and c = 6.'
      },
      {
        heading: 'Try factors before the formula.',
        paragraphs: ['Sometimes a quadratic is just two simpler equations in disguise. For x² − 5x + 6 = 0, find two numbers that multiply to 6 and add to −5: those numbers are −2 and −3.'],
        list: ['Factor: (x − 2)(x − 3) = 0.', 'A product is zero when at least one factor is zero.', 'So x = 2 or x = 3. Substitute each value into the original equation to check.']
      },
      {
        heading: 'A formula for every quadratic.',
        paragraphs: ['When the factors are not obvious, the quadratic formula gives the solutions directly. The expression under the square root, b² − 4ac, is called the discriminant.'],
        formula: 'x = (−b ± √(b² − 4ac)) / (2a)',
        list: ['If b² − 4ac > 0, there are two distinct real roots.', 'If b² − 4ac = 0, there is one repeated real root.', 'If b² − 4ac < 0, there are no real roots. Complex roots still exist.'],
        tip: 'The whole numerator is divided by 2a. Keep the brackets, watch the signs, and check your answers.'
      }
    ]
  },
  {
    id: 'newtons-laws',
    title: 'Newton’s laws, in plain English.',
    subject: 'physics',
    level: 'Class 9',
    minutes: 3,
    summary: 'Why things keep doing what they do — and what it takes to change that.',
    sections: [
      {
        heading: '1. Objects resist a change.',
        paragraphs: ['An object stays at rest, or keeps moving at a constant velocity, unless a net external force acts on it. This tendency to resist changes in motion is called inertia. A football does not stop because it runs out of force; friction and air resistance change its motion.'],
        tip: 'Net force means the vector sum of all external forces. Balanced forces do not mean that nothing is moving; they mean the velocity is not changing.'
      },
      {
        heading: '2. Force changes momentum.',
        paragraphs: ['The general form of Newton’s second law says that net force equals the rate of change of momentum. For an object of constant mass, this becomes the familiar F = ma. The acceleration points in the same direction as the net force.'],
        formula: 'F_net = ma  (constant mass)',
        list: ['A net force of 10 N on a 2 kg trolley gives an acceleration of 5 m/s².', 'Double the mass while keeping the force the same, and the acceleration halves.', 'Use kilograms, metres and seconds so that force comes out in newtons.']
      },
      {
        heading: '3. Forces come in pairs.',
        paragraphs: ['When object A exerts a force on object B, B exerts an equal and opposite force on A. These two forces act on different objects, so they do not cancel each other in the free-body diagram of one object.'],
        formula: 'F_A on B = −F_B on A',
        tip: 'When you push a wall, the wall pushes back on you. Label both the object applying the force and the object receiving it. That makes action–reaction pairs much easier to spot.'
      }
    ]
  },
  {
    id: 'the-mole',
    title: 'The mole is just a headcount.',
    subject: 'chemistry',
    level: 'Class 9',
    minutes: 3,
    summary: 'A friendly way into particles, molar mass, and those chemistry calculations.',
    sections: [
      {
        heading: 'A very big dozen.',
        paragraphs: ['Atoms are too small to count one at a time, so chemists count them in groups. A mole is an amount of substance containing exactly 6.02214076 × 10²³ specified elementary entities. That number is the Avogadro constant expressed in mol⁻¹.'],
        formula: '1 mol = 6.02214076 × 10²³ entities',
        tip: 'Always say what you are counting. One mole of oxygen atoms and one mole of oxygen molecules contain different numbers of atoms.'
      },
      {
        heading: 'Connect the lab to the particles.',
        paragraphs: ['The mass of one mole is the molar mass, usually measured in grams per mole. For a substance, its molar mass in g/mol is numerically equal to its relative atomic or molecular mass. Water has a molar mass of about 18.02 g/mol.'],
        formula: 'amount (mol) = mass (g) / molar mass (g/mol)',
        list: ['18.02 g of water is about 1 mol of water molecules.', '36.04 g of water is about 2 mol of water molecules.', 'Each water molecule has three atoms, so 1 mol of water contains about 3 mol of atoms.']
      },
      {
        heading: 'Let the units guide you.',
        paragraphs: ['You do not have to memorise every rearrangement. Start with the unit you have, multiply by a conversion factor, and check that the unwanted units cancel.'],
        list: ['Grams → moles: divide by molar mass.', 'Moles → particles: multiply by Avogadro’s number.', 'Particles → moles: divide by Avogadro’s number.'],
        tip: 'For 9.01 g of water: 9.01 ÷ 18.02 = 0.500 mol. That is about 3.01 × 10²³ water molecules.'
      }
    ]
  },
  {
    id: 'binary-search',
    title: 'Binary search: halve the hunt.',
    subject: 'computer-science',
    level: 'Foundations',
    minutes: 4,
    summary: 'Find a needle in a sorted haystack by throwing away half of it at a time.',
    sections: [
      {
        heading: 'Start in the middle.',
        paragraphs: ['Imagine looking for 23 in the sorted list [4, 8, 15, 16, 23, 42]. A linear search checks entries one by one. Binary search checks the middle and uses the ordering to rule out half of the remaining entries. The list must be sorted for this reasoning to work.'],
        list: ['Look at the middle value.', 'If it is the target, you are done.', 'If the target is smaller, keep the left half. If it is larger, keep the right half.', 'Repeat until you find the target or no entries remain.']
      },
      {
        heading: 'Keep the boundaries straight.',
        paragraphs: ['This version uses an inclusive lower bound and an exclusive upper bound: the search space is the indices from low up to, but not including, high.'],
        formula: 'low = 0; high = n; while low < high: mid = floor((low + high) / 2)',
        list: ['If values[mid] equals the target, return mid.', 'If values[mid] is less than the target, set low = mid + 1.', 'Otherwise, set high = mid.', 'If the loop ends, return −1 to mean “not found”.'],
        tip: 'In languages with fixed-size integers, use low + floor((high − low) / 2) to avoid overflow when adding two large indices.'
      },
      {
        heading: 'Why it is so quick.',
        paragraphs: ['Each comparison roughly halves the number of candidates. A sorted list of about a million entries needs at most about 20 comparisons in the worst case, because 2²⁰ is 1,048,576. That is logarithmic time, written O(log n).'],
        tip: 'Binary search uses O(1) extra space in its iterative form. If you need to sort first, include that cost too: sorting is not free.'
      }
    ]
  },
  {
    id: 'energy-conservation',
    title: 'Energy changes. It doesn’t vanish.',
    subject: 'physics',
    level: 'Class 9',
    minutes: 3,
    summary: 'Follow the energy from a raised ball to a falling one. The total has a story to tell.',
    sections: [
      {
        heading: 'A transformation, not a disappearance.',
        paragraphs: ['Energy can be transferred or transformed, but the total energy of an isolated system stays constant. When a moving object slows down because of friction, its mechanical energy has not vanished. Much of it has become internal energy in the object and its surroundings.'],
        tip: 'Define your system before doing the accounting. Energy can cross the boundary of a non-isolated system.'
      },
      {
        heading: 'The falling-ball story.',
        paragraphs: ['A ball held above the ground has gravitational potential energy. As it falls, that store decreases and its kinetic energy increases. If air resistance is negligible, the sum of the two stays constant.'],
        formula: 'mgh + ½mv² = constant',
        list: ['At the top of a drop from rest, speed is zero and potential energy is greatest.', 'Just before impact, height is smaller and speed is greater.', 'For a drop through height h from rest, v = √(2gh), neglecting air resistance.']
      },
      {
        heading: 'Try a number.',
        paragraphs: ['Drop a ball from 5 m and take g as 9.8 m/s². Its speed just before impact is √(2 × 9.8 × 5), which is about 9.9 m/s. The mass cancels, so under these assumptions a heavy and a light ball reach the same speed.'],
        tip: 'Real falls involve air resistance. Some mechanical energy is transferred to the air and the ball, so the ideal prediction is an approximation, not a universal rule.'
      }
    ]
  },
  {
    id: 'big-o',
    title: 'Big O, without the big mystery.',
    subject: 'computer-science',
    level: 'Foundations',
    minutes: 3,
    summary: 'A practical way to talk about how an algorithm grows with its input.',
    sections: [
      {
        heading: 'Think about growth, not a stopwatch.',
        paragraphs: ['Running an algorithm on your laptop gives one measurement. Big O describes an upper bound on how a resource requirement grows as the input becomes large, ignoring constant factors. It is often used for running time, but can also describe memory.'],
        tip: 'Say which resource and which case you mean. “O(n) time in the worst case” is more useful than just “this code is O(n)”.'
      },
      {
        heading: 'Three patterns you will see everywhere.',
        list: ['O(1): constant growth. Reading an array element by index does not require visiting the rest of the array.', 'O(n): linear growth. A single loop that checks every item once does work proportional to the number of items.', 'O(n²): quadratic growth. Two nested loops that each visit every item can do about n × n operations.'],
        paragraphs: ['If the input size doubles, a linear pattern roughly doubles, while a quadratic pattern roughly quadruples. Constant factors still matter for real programs, especially on small inputs.']
      },
      {
        heading: 'Count the work, then simplify.',
        paragraphs: ['Suppose an algorithm does 3n + 8 basic operations. For large n, the n term dominates the growth, so we describe it as O(n). For 2n² + 5n, the growth is O(n²).'],
        formula: '3n + 8 → O(n)     2n² + 5n → O(n²)',
        tip: 'Nested loops are not automatically O(n²). Check how many times the inner loop actually runs. Binary search is a good reminder to count the remaining work, not just the loop keywords.'
      }
    ]
  }
];
