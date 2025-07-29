#!/usr/bin/env bash

module add espresso/540-g-485-ompi-110

mpirun --allow-run-as-root -np 1 pw.x -in pw-scf.in &> pw-scf.out
mpirun --allow-run-as-root -np 1 pw.x -in pw-bands.in &> pw-bands.out
mpirun --allow-run-as-root -np 1 bands -in bands.in &> bands.out
mpirun --allow-run-as-root -np 1 pw.x -in pw-nscf.in &> pw-nscf.out
mpirun --allow-run-as-root -np 1 projwfc.x -in projwfc.in &> projwfc.out
