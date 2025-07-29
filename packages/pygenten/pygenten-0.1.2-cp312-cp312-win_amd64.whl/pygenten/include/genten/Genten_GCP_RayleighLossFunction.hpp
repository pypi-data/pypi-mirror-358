//@HEADER
// ************************************************************************
//     Genten: Software for Generalized Tensor Decompositions
//     by Sandia National Laboratories
//
// Sandia National Laboratories is a multimission laboratory managed
// and operated by National Technology and Engineering Solutions of Sandia,
// LLC, a wholly owned subsidiary of Honeywell International, Inc., for the
// U.S. Department of Energy's National Nuclear Security Administration under
// contract DE-NA0003525.
//
// Copyright 2017 National Technology & Engineering Solutions of Sandia, LLC
// (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are
// met:
//
// 1. Redistributions of source code must retain the above copyright
// notice, this list of conditions and the following disclaimer.
//
// 2. Redistributions in binary form must reproduce the above copyright
// notice, this list of conditions and the following disclaimer in the
// documentation and/or other materials provided with the distribution.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
// A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
// HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
// LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
// DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
// THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
// ************************************************************************
//@HEADER

#pragma once

#include <string>

#include "Genten_Util.hpp"
#include "Genten_AlgParams.hpp"

namespace Genten {

  class RayleighLossFunction {
  public:
    RayleighLossFunction(const AlgParams& algParams) :
      eps(algParams.loss_eps), pi_over_4(std::atan(ttb_real(1.0))) {}

    std::string name() const { return "Rayleigh"; }

    KOKKOS_INLINE_FUNCTION
    ttb_real value(const ttb_real& x, const ttb_real& m) const {
#if defined(__SYCL_DEVICE_ONLY__)
      using sycl::log;
#else
      using std::log;
#endif

      const ttb_real me = m + eps;
      return ttb_real(2.0)*log(me) + pi_over_4*(x/me)*(x/me);
    }

    KOKKOS_INLINE_FUNCTION
    ttb_real deriv(const ttb_real& x, const ttb_real& m) const {
      const ttb_real me = m + eps;
      return ttb_real(2.0)*(ttb_real(1.0)/me - pi_over_4*(x/me)*(x/(me*me)));
    }

    KOKKOS_INLINE_FUNCTION static constexpr bool has_lower_bound() { return true; }
    KOKKOS_INLINE_FUNCTION static constexpr bool has_upper_bound() { return false; }
    KOKKOS_INLINE_FUNCTION static constexpr ttb_real lower_bound() { return 0.0; }
    KOKKOS_INLINE_FUNCTION static constexpr ttb_real upper_bound() { return DOUBLE_MAX; }

  private:
    ttb_real eps;
    ttb_real pi_over_4;
  };

}
