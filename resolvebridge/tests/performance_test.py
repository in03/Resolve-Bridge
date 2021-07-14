import cProfile
import pstats

def performance_test(function_to_test):
    """ Quick and dirty performance test using profiling """


    pr = cProfile.Profile()
    pr.enable()

    function_to_test()

    pr.disable()

    stats = pstats.Stats(pr)
    # stats.sort_stats(pstats.SortKey.TIM
    stats.print_stats()

    print("[  DONE  ]")

if __name__ == "__main__":

    from resolvebridge import app

    performance_test(app)
