

def testthrow():
    assert False


if __name__ == '__main__':
    try:
        testthrow()
        print('should not get here')

    except AssertionError:
        print("got it")
    else:
        print("error")

    print("done")
