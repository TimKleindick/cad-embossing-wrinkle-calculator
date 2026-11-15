"""Independent golden-section oracle; does not reuse production numerics.

Run with python -m tools.independent_check. Deliberately slower than the core.
"""
import math
import json
import time

def cosine_len(a, n):
    prev=0.0
    total=0.0
    for k in range(1,n+1):
        y=a*(1-math.cos(2*math.pi*k/n))
        total+=math.hypot(1/n,y-prev)
        prev=y
    return total

def amplitude(ratio, n=1000):
    lo=0.0; hi=1.0
    while cosine_len(hi,n)<ratio: hi*=2
    for _ in range(58):
        mid=(lo+hi)/2
        if cosine_len(mid,n)<ratio: lo=mid
        else: hi=mid
    return (lo+hi)/2

def shape(u,q,phi):
    u=min(u,1-u)
    sn=math.sin(phi); cs=math.cos(phi)
    rho=q/(4*sn)
    u1=q/4; u2=0.5-q/4
    height=(1-q)*math.tan(phi)/2+q*math.tan(phi/2)/2
    if u<=u1:
        return u*u/(rho+math.sqrt(max(0,rho*rho-u*u))) if u else 0.0
    if u<=u2:
        y1=rho*(1-cs)
        return y1+(u-u1)*sn/cs
    v=0.5-u
    return height-v*v/(rho+math.sqrt(max(0,rho*rho-v*v)))

def golden(fun,lo,hi,tol=2e-12):
    gr=(math.sqrt(5)-1)/2
    x1=hi-gr*(hi-lo); x2=lo+gr*(hi-lo)
    f1=fun(x1); f2=fun(x2)
    while hi-lo>tol:
        if f1>f2:
            lo=x1; x1=x2; f1=f2
            x2=lo+gr*(hi-lo); f2=fun(x2)
        else:
            hi=x2; x2=x1; f2=f1
            x1=hi-gr*(hi-lo); f1=fun(x1)
    x=(lo+hi)/2
    return x,fun(x)

def fit(a,n=1000):
    # Symmetric squared residual sum, exact same 1001 nodes and weights.
    samples=[(k/n, a*(1-math.cos(2*math.pi*k/n)), 1 if k==n//2 or k==0 else 2) for k in range(n//2+1)]
    def obj(q,p):
        return math.fsum(w*(shape(u,q,p)-y)**2 for u,y,w in samples)
    def minimize_q(p):
        return golden(lambda q:obj(q,p),1e-10,1-1e-10)
    # Bound optimum with coarse phi scan, then golden.
    scan=[]
    for k in range(1,50):
        p=k*math.pi/100
        q,sse=minimize_q(p)
        scan.append((sse,p,q))
    best=min(scan)
    p,sse=golden(lambda p:minimize_q(p)[1],max(1e-8,best[1]-math.pi/100),min(math.pi/2-1e-8,best[1]+math.pi/100))
    q,sse=minimize_q(p)
    return q,p,sse,[(s,p,q) for s,p,q in sorted(scan)[:3]]

def report(l1=40,l2=30,n=1000):
    a=amplitude(l1/l2,n)
    q,p,sse,_=fit(a,n)
    r=q*l2/(4*math.sin(p))
    s=(l2/2-2*r*math.sin(p))/math.cos(p)
    h=l2*shape(0.5,q,p)
    pts=[l2*shape(k/n,q,p) for k in range(n+1)]
    poly=math.fsum(math.hypot(l2/n,pts[k]-pts[k-1]) for k in range(1,n+1))
    err=[pts[k]-l2*a*(1-math.cos(2*math.pi*k/n)) for k in range(n+1)]
    rr_excel=l2*l2/(2*math.pi**2*(a*l2))
    rr_true=rr_excel/2
    return dict(l1=l1,l2=l2,n=n,A=a*l2,R=r,phi_deg=math.degrees(p),h=h,s=s,q=q,polygon=poly,analytic=4*r*p+2*s,SSE=sse*l2*l2,rmse=math.sqrt(sse/(n+1))*l2,max_error=max(abs(v) for v in err),length_delta_pct=100*(poly/l1-1),excel_radius=rr_excel,true_radius=rr_true,strain_excel_pct=100/rr_excel,strain_true_pct=100/rr_true,strain_arc_pct=100/r)

if __name__ == '__main__':
    result = report()
    print(json.dumps(result,indent=2))
    from wrinkle.core import calculate
    actual = calculate(40,30,2)
    for own,key in [('A','amplitude_mm'),('R','radius_mm'),('h','height_mm'),
                    ('s','straight_mm'),('polygon','fit_polygon_mm'),
                    ('analytic','fit_analytic_mm'),('phi_deg','phi_deg')]:
        assert abs(result[own]-actual[key]) < 1e-6, (own,result[own],actual[key])
    # Independent composite Simpson integration of the continuous cosine arc.
    n=8000
    a=result['A']/30
    integrand=lambda u: math.sqrt(1+(2*math.pi*a*math.sin(2*math.pi*u))**2)
    integral=30/(3*n)*math.fsum((1 if i in (0,n) else 4 if i%2 else 2)*integrand(i/n) for i in range(n+1))
    assert abs(integral-40.000027699761) < 1e-9, integral
    print('PASS: independent golden-section fit and continuous-cosine Simpson integration',integral)
